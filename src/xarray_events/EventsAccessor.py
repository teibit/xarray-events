"""Definition of the :class:`EventsAccessor` class.

Define the :class:`EventsAccessor` class with enough methods to act as a
wrapper around xarray extending its functionality to better support events data.

"""
from __future__ import annotations
import collections.abc as collections
import math
import numbers

import numpy as np
import pandas as pd
import typing
import warnings
import xarray as xr


@xr.register_dataset_accessor('events')
class EventsAccessor:
    """xarray accessor with extended events-handling functionality.

    An xarray accessor that extends its functionality to handle events in a
    high-level way. This API makes it easy to load events into an existing
    :obj:`Dataset` from a :obj:`DataFrame` and perform selections on the events
    satisfying a set of specified constraints.

    Attributes:
        :attr:`_ds`: The :obj:`Dataset` to be accessed whose class-level
        functionality is to be extended.

    """

    def __init__(self, ds: xr.Dataset) -> None:
        """Init for :class:`EventsAccessor` given a :obj:`Dataset`."""
        self._ds = ds

    @property
    def df(self) -> pd.DataFrame:
        """Manage the events :obj:`DataFrame`.

        Note: Getting it when it doesn't exist raises an exception. Setting it
        when it *apparently* already exists raises a warning.

        """
        try:
            return self._ds.attrs['_events']
        except KeyError:
            raise TypeError('Events not yet loaded.')

    @df.setter
    def df(self, events: pd.DataFrame) -> None:
        if '_events' in self._ds.attrs:
            warnings.warn(
                "Attempting to load events despite _events being already an "
                "attribute of the Dataset."
            )

        self._ds.attrs['_events'] = events

    def _flatten_list_tuples_strings(
        self,
        dict_view_mapping_values: typing.ValuesView[
            typing.Union[
                typing.Tuple[typing.Hashable, typing.Hashable], typing.Hashable
            ]
        ]
    ) -> typing.List[typing.Hashable]:
        """Flatten a list of tuples and other hashables.

        This method is needed because the values in :attr:`ds_df_mapping` can be
        either a tuple or some arbitrary hashable (usually a str), so
        appropriate checks need to be performed since it's not trivial to get
        them directly.

        In the future, we should probably also check for the structure of the
        given tuples and hashables.

        """
        df_given: typing.List[typing.Hashable] = list()
        mapping_values = list(dict_view_mapping_values).copy()

        for val in mapping_values:

            if isinstance(val, typing.List):
                for x in val:
                    mapping_values.append(x)
                continue

            if isinstance(val, typing.Tuple):  # type: ignore
                df_given.extend(val)  # type: ignore

            else:
                df_given.append(val)

        return df_given

    @property
    def ds_df_mapping(self) -> typing.Mapping[
        typing.Hashable,
        typing.Union[
            typing.Tuple[typing.Hashable, typing.Hashable], typing.Hashable
        ]
    ]:
        """Manage the mapping from :obj:`Dataset` to :obj:`DataFrame`.

        Note: Getting it when it doesn't exist raises an exception. Setting it
        when it *apparently* already exists raises a warning.

        This is basically a dictionary where a key is a :obj:`Dataset` dimension
        or coordinate and a value is a tuple or a string referring to an events
        :obj:`DataFrame` column. The reason behind its existence is that it is a
        non-trivial task to *automatically* deduce such correspondances which
        are needed for some operations with events. This dictionary is provided
        as an argument to :meth:`load`.

        """
        try:
            return self._ds.attrs['_ds_df_mapping']  # type: ignore
        except KeyError:
            raise TypeError('Mapping not yet loaded.')

    @ds_df_mapping.setter
    def ds_df_mapping(
        self,
        mapping: typing.Mapping[
            typing.Hashable,
            typing.Union[
                typing.Tuple[typing.Hashable, typing.Hashable], typing.Hashable
            ]
        ]
    ) -> None:
        # Case where the mapping already seems to exist yet a new one is
        # trying to be loaded.
        if '_ds_df_mapping' in self._ds.attrs:
            warnings.warn(
                "Attempting to load the ds-df mapping despite _ds_df_mapping "
                "being already an attribute of the Dataset.", UserWarning
            )

        df_given = set(self._flatten_list_tuples_strings(mapping.values()))
        df_real = set(self.df)

        ds_given = set(mapping)
        ds_real = set(self._ds) | set(self._ds.coords)

        # If any unrecognizable key (events DataFrame column) is given.
        if not df_given <= df_real:
            raise ValueError(
                f"Invalid mapping. None of {df_given - df_real} are event "
                f"DataFrame columns.")

        # If any unrecognizable value (Dataset Dimension or Coordinate) is
        # given.
        if not ds_given <= ds_real:
            raise ValueError(
                f"Invalid mapping. None of {ds_given - ds_real} are "
                f"Dataset dimensions or coordinates.")

        # At this point we're certain that the given mapping is valid.
        self._ds.attrs['_ds_df_mapping'] = mapping

    @property
    def duration_mapping(self) -> typing.Optional[
        typing.Tuple[
            typing.Hashable, typing.Tuple[typing.Any, ...]
        ]
    ]:
        """Manage the events column pairs that represent a duration.

        This property is automatically deduced from (and therefore depends on)
        :attr:`ds_df_mapping`.

        """
        # Only the *one* tuple that maps to Dataset coordinates represents
        # properly a duration, at least for now. We then define a duration as a
        # reduced version of self.ds_df_mapping only containing that.
        mappings_with_durations = [
            (key, val)
            for key, val in self.ds_df_mapping.items() if isinstance(val, tuple)
        ]

        if not mappings_with_durations:
            return None

        if len(mappings_with_durations) > 1:
            raise ValueError('More than one duration attribute pairs given.')

        return mappings_with_durations[0]

    def _load_events_from_DataFrame(self, df: pd.DataFrame) -> None:
        # If source is a DataFrame, assign it directly as an attribute of _ds.
        self._ds = self._ds.assign_attrs(_events=df)

    def _is_column_mask(
        self, val: collections.Collection[typing.Hashable], col: pd.Series
    ) -> bool:
        # Checks whether a Collection is a boolean mask of a Dataframe column.
        return len(val) == len(col) and all(type(x) == bool for x in val)

    def _filter_events(
        self,
        key: typing.Hashable,
        value: typing.Union[
            collections.Callable[[pd.Series], pd.Series],
            collections.Collection[typing.Hashable]
        ]
    ) -> None:
        # We need to disable the warnings that will be thrown due to calling the
        # setter df since they aren't meaningful in this case.
        warnings.filterwarnings('ignore')

        # Case where the specified value is a "single value", which is anything
        # that's neither a Collection nor a Callable.
        # We ignore this line because of:
        # https://github.com/python/mypy/issues/6864
        if (
            not (
                isinstance(value, collections.Collection) and
                not isinstance(value, typing.Hashable)
            ) and
            not isinstance(value, collections.Callable)  # type: ignore
        ):
            self.df = self._ds._events[self._ds._events[key] == value]

        # Case where the specified value is a Collection but not a boolean mask.
        # Notice that a boolean mask is a special kind of Collection!
        elif (
            isinstance(value, collections.Collection) and not
            self._is_column_mask(value, self._ds._events[key])
        ):
            self.df = self._ds._events[self._ds._events[key].isin(value)]

        # Case where the specified value is a boolean mask or a Callable that
        # when applied can be converted into one.
        else:
            if isinstance(value, collections.Callable):  # type: ignore
                value_transformed = value(self._ds._events[key])  # type: ignore

                if self._is_column_mask(
                    value_transformed, self._ds._events[key]
                ):
                    self.df = self._ds._events[value_transformed.values]

        warnings.filterwarnings('always')  # Reactivate warnings.

    def _get_ds_from_df(
        self, df_col: typing.Optional[typing.Hashable]
    ) -> typing.Optional[typing.Hashable]:
        """Get key from value in self.ds_df_mapping.

        This method will return the key (Dataset coordinate or dimension) of
        some entry in self.ds_df_mapping if the corresponding value (Dataframe
        column) matches :data:`df_col`.

        This method is needed because the values in self.ds_df_mapping can be
        either str or tuple, so appropriate checks need to be performed since
        it's not trivial to get this correspondance directly.

        """
        mapping = list(self.ds_df_mapping.items()).copy()

        for key, val in mapping:

            if isinstance(val, typing.List):
                for x in val:
                    mapping.append((key, x))
                mapping.remove((key, val))

        for key, val in mapping:

            if (
                (df_col == val) or
                (isinstance(val, tuple) and df_col in [val[0], val[1]])
            ):
                return key

        return None

    def _slice_ds_by_duration(
        self, start: typing.Hashable, end: typing.Hashable
    ) -> typing.List[typing.Hashable]:
        """Silce a :obj:`Dataset` by the duration values.

        This method will slice a Dataset dimension or coordinate by the duration
        values, which can be of any type and need not be sortable.

        """
        values = list(self._ds[self.duration_mapping[0]].values)  # type: ignore

        return values[values.index(start):(values.index(end) + 1)]

    def _slice_ds_indexes_by_duration(
        self, start: typing.Hashable, end: typing.Hashable
    ) -> typing.Iterable[slice]:
        """Silce a :obj:`Dataset` by the duration values.

        This method will slice a Dataset dimension or coordinate by the duration
        values, which can be of any type and need not be sortable.

        """
        values = list(self._ds[self.duration_mapping[0]].values)  # type: ignore

        return list(
            range(values.index(start), (values.index(end) + 1))  # type: ignore
        )

    def df_contains_overlapping_events(self) -> bool:
        """Decide whether the events in the DataFrame overlap."""
        if not self.duration_mapping:
            raise TypeError('No duration mapping given.')

        row_iterator = (
            self.df.sort_values(self.duration_mapping[1][0]).itertuples()
        )

        for item in row_iterator:

            # Check whether the difference between the start of the next event
            # and the end of the current one less than 1, in which case they
            # overlap.
            next_event = next(row_iterator, math.inf)

            start = self.duration_mapping[1][0]
            end = self.duration_mapping[1][1]

            if getattr(next_event, start) - getattr(item, end) < 1:
                return True

        return False

    def df_contains_gaps(self) -> bool:
        """Decide whether the events DataFrame contains gaps.

        This method will check whether the range spanned by the duration of all
        events is the same as the Dataset coordinate values range, in which case
        we can conclude that the events cover the whole coordinate and therefore
        contain no gaps.

        """
        if self.duration_mapping is None:
            raise TypeError('No duration mapping loaded.')

        ds_values_range = set(
            self._ds[self.duration_mapping[0]].to_series()
        )
        df_values_range: typing.Set[typing.Hashable] = set()

        for item in self.df.itertuples():

            start = getattr(item, self.duration_mapping[1][0])
            end = getattr(item, self.duration_mapping[1][1])

            df_values_range |= set(self._slice_ds_by_duration(start, end))

        return ds_values_range != df_values_range

    def fill_gaps(
        self,
        event_type_col_name: typing.Optional[str] = 'event_type',
        event_type_col_value: typing.Optional[str] = 'default',
        extra_col_val_pairs: typing.Mapping[
            typing.Optional[str], typing.Optional[typing.Hashable]
        ] = dict()
    ) -> xr.Dataset:
        """Fill the gaps in the events :obj:`DataFrame`.

        This method will identify the gaps on the events :obj:`DataFrame` and
        fill them by creating a new event for each gap. To identify the gaps,
        the ds-df mapping must have been previously given to :meth:`load`.

        Args:
            :attr:`event_type_col_name`: name of the column in the events
                :obj:`DataFrame` that identifies the events. Defaults to
                `event_type` if unspecified.

            :attr:`event_type_col_value`: type of the new events. Defaults to
                `default` if unspecified.

            :attr:`extra_col_val_pairs`: a dictionary containing any new column
                with values to be appended.

        Returns:
            A modified version of the Dataset containing the events
            :obj:`DataFrame` with no gaps.

        """
        if self.duration_mapping is None:
            raise TypeError('No duration mapping loaded.')

        # Get the Dataset coordinate values that the "duration" attributes
        # match to as a Series. We want to be able to tell whether each element
        # on this set corresponds to (or is covered by) some event.
        ds_values_range = pd.Series(self._ds[self.duration_mapping[0]].values)

        df_values_range = list()

        for item in self.df.itertuples():

            start = getattr(item, self.duration_mapping[1][0])
            end = getattr(item, self.duration_mapping[1][1])

            # Get all values spanned by the duration attributes of the events.
            df_values_range.extend(self._slice_ds_by_duration(start, end))

        gaps: typing.List[typing.Any] = list()
        gap: typing.List[typing.Hashable] = list()

        # Construct a Series in which each index is a value from ds_values_range
        # and each value is a boolean that represents whether there exists a
        # corresponding value in df_values_range, effectively indicating whether
        # that value is a gap.
        gap_series = (
            pd.Series(sorted(df_values_range))
            .reset_index()
            .set_index(0)
            .reindex(ds_values_range)
            ['index']
            .map(lambda x: np.isnan(x))
        )

        for ds_val, is_gap in gap_series.iteritems():

            if not is_gap:  # If the current ds_val does not represent a gap.
                if gap:
                    gaps.append(gap)
                gap = list()
                continue

            gap.append(ds_val)  # Append all ds_val from the current gap.

        else:
            if gap:  # Append final gap.
                gaps.append(gap)

            # Reduce the gaps to simply the endpoints of every group.
            # The endpoints correspond to the "duration" Dataframe attributes.
            gaps = [(val[0], val[-1]) for val in gaps if val]

        # We need to disable the warnings that will be thrown due to calling the
        # setter df since they aren't meaningful in this case.
        warnings.filterwarnings('ignore')

        for gap in gaps:

            self.df.index.name = event_type_col_name

            self.df = self.df.append(  # Why does this not happen in-place?!
                pd.Series(
                    {
                        self.duration_mapping[1][0]: gap[0],
                        self.duration_mapping[1][1]: gap[1],
                        event_type_col_name: event_type_col_value,
                        **extra_col_val_pairs
                    }
                ), ignore_index=True
            )

            # Reset the index of the events DataFrame after having appended a
            # row for a new event.
            self.df = self.df.reset_index(drop=True)

        warnings.filterwarnings('always')  # Reactivate warnings.

        return self._ds  # Gaps are now filled in the internal DataFrame.

    def expand_to_match_ds(
        self,
        dimension_matching_col: typing.Hashable,
        fill_method: typing.Optional[typing.Hashable] = None,
        fill_value_col: typing.Hashable = 'event_index'
    ) -> xr.DataArray:
        """Expand a :obj:`DataFrame` column to match the shape of the :obj:`Dataset`.

        Given the column :attr:`dimension_matching_col` of the events
        :obj:`DataFrame` whose values form a subset of the values of a
        :obj:`Dataset` dimension or coordinate, this method will create a
        :obj:`DataArray` in such a way that its coordinates are the values of
        the aforementioned superset and the values are given by the column
        :attr:`fill_value_col` of the events :obj:`DataFrame`, filling in the
        emerging gaps as per :attr:`fill_method`.

        This subset-superset correspondance is a *mapping* (key-value pair) from
        a column of the events :obj:`DataFrame` (key) to a :obj:`Dataset`
        dimension or coordinate (value), and it must be previously specified in
        a dictionary upon calling :meth:`load`. It is handled by the
        :meth:`ds_df_mapping` property.

        Call this method strictly after having called :meth:`load` with the
        :obj:`ds_df_mapping` argument.

        Args:
            :attr:`dimension_matching_col`: Events :obj:`DataFrame` column whose
                values form a subset of the values of some :obj:`Dataset`
                dimension or coordinate and will be expanded to match them. This
                argument uses a mapping from a column of the events
                :obj:`DataFrame` to a :obj:`Dataset` dimension or coordinate
                that must have already been specified upon calling :meth:`load`.
            :attr:`fill_method`: Method to be used to fill the gaps that emerge
                after expanding :attr:`dimension_matching_col`. The possible
                filling methods are:

                -   None (default): don't fill gaps.
                -   pad / ffill: Propagate values forward until next one.
                -   backfill / bfill: Use next value to fill gap.
                -   nearest: Use nearest values to fill gap.
            :attr:`fill_value_col`: Events :obj:`DataFrame` column whose values
                fill the output array.

        Returns:
            A :obj:`DataArray` created as specified above.

        Raises:
            KeyError: when either :attr:`dimension_matching_col` or
                :attr:`fill_value_col` is unrecognizable.

        Example:
            See :doc:`../../tutorials/sports_data/expand_to_match_ds`.

        """
        # Besides the index name, we also add event_index as a dummy to the list
        # of cols to handle the case where this method is called by another
        # method and therefore neither reset_index nor rename have been called
        # on self.df yet.
        df_cols_expanded = list(self.df) + [self.df.index.name, 'event_index']

        if (
            (dimension_matching_col not in df_cols_expanded) or
            (fill_value_col not in df_cols_expanded)
        ):
            raise KeyError(
                f"None of {[dimension_matching_col] + [fill_value_col]} "
                f"are columns of the events DataFrame."
            )

        return xr.DataArray(
            self.df
            .sort_values(dimension_matching_col)
            .reset_index()
            .rename(columns={'index': fill_value_col}, errors='ignore')
            .set_index(dimension_matching_col, drop=False)
            [fill_value_col]
            .reindex(
                self._ds[self._get_ds_from_df(dimension_matching_col)],
                method=fill_method
            )
        )

    def groupby_events(
        self,
        array_to_group: typing.Hashable,
        dimension_matching_col: typing.Optional[typing.Hashable] = None,
        fill_method: typing.Optional[typing.Hashable] = None
    ) -> xr.core.groupby.DataArrayGroupBy:
        """Group a data variable by the events in the :obj:`DataFrame`.

        This method uses a :obj:`DataArray` generated by
        :meth:`expand_to_match_ds` to group a :attr:`DataVariable` of the
        :obj:`Dataset`, resulting in a :obj:`GroupBy` object on which
        functions can be called.

        Call this method strictly after having called :meth:`load` with the
        :obj:`ds_df_mapping` argument.

        Args:
            :attr:`array_to_group`: :obj:`Dataset` data variable or coordinate
                to group.
            :attr:`dimension_matching_col`: Events :obj:`DataFrame` column whose
                values form a subset of the values of some :obj:`Dataset`
                dimension or coordinate and will be expanded to match them. This
                argument uses a mapping from a column of the events
                :obj:`DataFrame` to a :obj:`Dataset` dimension or coordinate
                that must have already been specified upon calling :meth:`load`.
            :attr:`fill_method`: Method to be used to fill the gaps that emerge
                after expanding :attr:`dimension_matching_col`. The possible
                filling methods are:

                -   pad / ffill: Propagate values forward until next one.
                -   backfill / bfill: Use next value to fill gap.
                -   nearest: Use nearest values to fill gap.

        Returns:
            A :obj:`DataArrayGroupBy` object, which is internally just like
            :obj:`GroupBy` from :mod:`pandas`.

        Raises:
            KeyError: when :attr:`dimension_matching_col` is unrecognizable.

        Example:
            See :doc:`../../tutorials/sports_data/groupby_events`.

        """
        if self.duration_mapping is None:
            raise TypeError('No duration mapping loaded.')

        # If only array_to_group is given, we can still group it so long as a
        # duration has been properly specified on load.
        if (
            self.ds_df_mapping and
            not dimension_matching_col and
            not fill_method
        ):
            dimension_matching_col = self.duration_mapping[1][0]
            fill_method = 'ffill'

        # If dimension_matching_col matches to nothing in self.ds_df_mapping.
        if not self._get_ds_from_df(dimension_matching_col):
            raise KeyError(
                f"No match found for {dimension_matching_col} "
                f"in ds_df_mapping."
            )

        # Construct groups -- a GroupBy object. The object it refers to is
        # array_to_group and the groups are given by the events.
        groups: xr.core.groupby.DataArrayGroupBy = (
            self._ds
            [array_to_group]
            .groupby(
                self.expand_to_match_ds(
                    dimension_matching_col,  # type: ignore
                    fill_method,
                    self.df.index.name or 'event_index'
                )
            )
        )

        # If there are overlapping events or gaps, groups is actually invalid
        # because its groups get trimmed and hence the overlapping area is lost
        # or they cover more data than they should. This is how groupby works by
        # default. To get around this, we modify its attribute _group_indices to
        # include all coordinate values thereby accounting for repetitions.
        if self.df_contains_overlapping_events() or self.df_contains_gaps():

            for event in self.df.itertuples():

                start = getattr(event, self.duration_mapping[1][0])
                end = getattr(event, self.duration_mapping[1][1])

                groups._group_indices[
                    getattr(event, 'Index')
                ] = self._slice_ds_indexes_by_duration(start, end)

        return groups

    def load(
        self,
        source: pd.DataFrame,
        ds_df_mapping: typing.Optional[
            typing.Mapping[
                typing.Hashable,
                typing.Union[
                    typing.Tuple[typing.Hashable, typing.Hashable],
                    typing.Hashable
                ]
            ]
        ] = None
    ) -> xr.Dataset:
        """Set the events :obj:`DataFrame` as an attribute of the :obj:`Dataset`.

        This is the first method that should be called on a :obj:`Dataset` when
        using this API. The internal attribute it creates in the :obj:`Dataset`
        is :attr:`_events`.

        Optionally, :attr:`ds_df_mapping` can be specified. This dictionary
        consists of key-value pairs that establish a correspondance between an
        events :obj:`DataFrame` column and a :obj:`Dataset` dimension or
        coordinate, which is needed for some operations on events.

        To facilitate the task of referencing :attr:`_events`, we provide the
        *property* :meth:`df`. Assuming you have a :obj:`Dataset` called
        ``ds``, you may use it via ``ds.events.df``.

        Args:
            :attr:`source`: A :obj:`DataFrame` specifying where the events are
                to be loaded from.

            :attr:`ds_df_mapping`: An optional dictionary where the keys are
                columns from the events :obj:`DataFrame` and the values are
                dimensions or coordinates from the :obj:`Dataset` thereby
                specifying a *mapping* between them.

        Returns:
            The modified :obj:`Dataset` now including events as an attribute.

        Raises:
            ValueError: on an invalid mapping.

        Example:
            See :doc:`../../tutorials/sports_data/loading`.

        """
        # A DataFrame is the ultimate way of representing the events.
        if isinstance(source, pd.DataFrame):
            self._load_events_from_DataFrame(source)

        if ds_df_mapping:
            self.ds_df_mapping = ds_df_mapping

        return self._ds

    def sel(
        self,
        indexers: typing.Optional[
            typing.Mapping[str, typing.Any]
        ] = None,
        method: typing.Optional[str] = None,
        tolerance: typing.Optional[numbers.Number] = None,
        drop: bool = False,
        **indexers_kwargs: typing.Any
    ) -> xr.Dataset:
        """Perform a selection on :attr:`_ds` given specified constraints.

        This is a wrapper around :meth:`xr.Dataset.sel` that extends its
        functionality to support events handling.

        The arguments that match events :obj:`DataFrame` attributes are used to
        filter the events. Everything else is passed directly to
        :meth:`xr.Dataset.sel`.

        Call this method by specifying constraints for both the :obj:`Dataset`
        dimensions and the events :obj:`DataFrame` attributes in a single
        dictionary.

        The values for the constraints may be of different types, and the
        behavior varies accordingly. Here's how it works:

        -   If the value is a *single value*, filter by it directly.

        -   If the value is an instance of :class:`Collection` (like a list),
            filter the events by them.

        -   If the value is a *boolean mask*, filter the :obj:`DataFrame` by it.
            In case the value is an instance of :class:`Callable` (like a lambda
            function), apply the function to the events :obj:`DataFrame` to
            obtain a mask first.

        Tip: If intended to be chained, call after having called :meth:`load`
        to ensure that the events are properly loaded.

        The arguments, return values and raised exceptions are the same as for
        :mod:`xr.Dataset.sel`, in order to stay true to the wrapper nature of
        this method. See the `official xarray documentation
        <http://xarray.pydata.org/en/stable/generated/xarray.Dataset.sel.html>`_
        for details.

        Example:
            See :doc:`../../tutorials/sports_data/selecting/index`.

        """
        indexers_kwargs.update(indexers or {})

        # Constraints may refer to either Dataset dimensions or events
        # attributes.
        constraints = indexers_kwargs

        # Events attributes, which may not exist.
        events = list(
            self.df.columns if '_events' in self._ds.attrs else []
        )

        # Dataset dimensions and coordinates.
        ds = list(self._ds) + list(self._ds.dims)

        constraints_sel = list()
        constraints_events = list()
        unknown_constraints = list()

        # Analyze each constraint individually to decide whether it should be
        # used to filter the Dataset or the events DataFrame.
        for constraint, value in constraints.items():

            if constraint in events:
                constraints_events.append(constraint)

            if constraint in ds:
                constraints_sel.append(constraint)

            if constraint not in (events + ds):
                unknown_constraints.append(constraint)

        if unknown_constraints:
            raise KeyError(
                f"Unrecognizable constraints: {unknown_constraints}."
            )

        # Call xr.Dataset.sel with the method args as well as all constraints
        # that match Dataset dimensions or coordinates.
        self._ds = self._ds.sel(
            indexers={
                k: v for k, v in constraints.items() if k in constraints_sel
            },
            method=method,  # type: ignore
            tolerance=tolerance,  # type: ignore
            drop=drop
        )

        # Filter the events DataFrame with the constraints that match columns.
        for k, v in {
            k: v for k, v in constraints.items() if k in constraints_events
        }.items():
            self._filter_events(k, v)

        # TODO: Here's a good place to drop "out-of-view" events.

        return self._ds
