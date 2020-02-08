"""Definition of the :py:class:`EventsAccessor` class.

Define the :py:class:`EventsAccessor` class with enough methods to act as a
wrapper around xarray extending its functionality to better support events data.

"""
from __future__ import annotations

from collections.abc import Collection, Callable
from pathlib import Path
from numbers import Number
from typing import Any, Hashable, Mapping, Optional, Union
from warnings import filterwarnings, warn

from pandas import DataFrame
from pandas import Series
from xarray import Dataset
from xarray import DataArray
from xarray import register_dataset_accessor
from xarray.core.groupby import DataArrayGroupBy


@register_dataset_accessor('events')
class EventsAccessor:
    """xarray accessor with extended events-handling functionality.

    An xarray accessor that extends its functionality to handle events in a
    high-level way. This API makes it easy to load events into an existing
    :py:obj:`Dataset` from a variety of sources and perform selections on the
    events satisfying a set of specified constraints.

    Attributes:
        _ds: The :py:obj:`Dataset` to be accessed whose class-level
        functionality is to be extended.

    """

    def __init__(self, ds: Dataset) -> None:
        """Init :py:class:`EventsAccessor` with a :py:obj:`Dataset`."""
        self._ds = ds

    @property
    def df(self) -> DataFrame:
        """Manage the events :py:obj:`DataFrame` of :py:attr:`_ds`.

        Note: Getting it when it doesn't exist raises an exception. Setting it
        when it *apparently* already exists raises a warning.

        """
        try:
            return self._ds.attrs['_events']
        except KeyError:
            raise TypeError('Events not yet loaded')

    @df.setter
    def df(self, events: DataFrame) -> None:
        if '_events' in self._ds.attrs:
            warn('Attempting to load events despite _events being already an '
                 'attribute of the Dataset.')
        self._ds.attrs['_events'] = events

    @property
    def df_ds_mapping(self) -> DataFrame:
        """Manage the mapping from :py:obj:`DataFrame` to :py:obj:`Dataset`.

        Note: Getting it when it doesn't exist raises an exception. Setting it
        when it *apparently* already exists raises a warning.

        This is basically a dictionary where a key is an events
        :py:obj:`DataFrame` column and a value is a :py:obj:`Dataset` dimension
        or coordinate. The reason behind its existence is that it is a
        non-trivial task to *automatically* deduce such correspondances which
        are needed for some operations with events. This dictionary is provided
        as an argument to :py:meth:`load`.

        """
        try:
            return self._ds.attrs['_df_ds_mapping']
        except KeyError:
            raise TypeError('Mapping not yet loaded')

    @df_ds_mapping.setter
    def df_ds_mapping(self, mapping: dict) -> None:
        # Case where the mapping already seems to exist yet a new one is
        # trying to be loaded.
        if '_df_ds_mapping' in self._ds.attrs:
            warn('Attempting to load the df-ds mapping despite _df_ds_mapping '
                 'being already an attribute of the Dataset.')

        df_given = set(mapping)
        df_real = set(self.df)

        ds_given = set(mapping.values())
        ds_real = set(self._ds) | set(self._ds.coords)

        # If any unrecognizable key (events DataFrame column) is given.
        if not df_given <= df_real:
            raise ValueError(
                f'Invalid mapping. None of {df_given - df_real} are event '
                'DataFrame columns.')

        # If any unrecognizable value (Dataset Dimension or Coordinate) is
        # given.
        if not ds_given <= ds_real:
            raise ValueError(
                f'Invalid mapping. None of {ds_given - ds_real} are '
                'Dataset dimensions or coordinates.')

        # At this point we're certain that the given mapping is valid.
        self._ds.attrs['_df_ds_mapping'] = mapping

    def _load_events_from_DataFrame(self, df: DataFrame) -> None:
        # If source is a DataFrame, assign it directly as an attribute of _ds.
        self._ds = self._ds.assign_attrs(_events=df)

    def _load_events_from_csv(self) -> None:
        pass

    def _load_events_from_Path(self, p: Path) -> None:
        # If source is a Path, calls the right handler depending on the
        # extension.
        if p.suffix == '.csv':
            self._load_events_from_csv()
        pass

    def _is_column_mask(self, val: Collection, col: Series) -> bool:
        # Checks whether a Collection is a boolean mask of a Dataframe column.
        return len(val) == len(col) and all(type(x) == bool for x in val)

    def _filter_events(self, k: str, v) -> None:
        # We need to disable the warnings that will be thrown due to calling the
        # setter df since they aren't meaningful in this case.
        filterwarnings('ignore')

        # Case where the specified value is a "single value", which is anything
        # that's neither a Collection nor a Callable.
        # We ignore this line because of:
        # https://github.com/python/mypy/issues/6864
        if (
            not (isinstance(v, Collection) and not isinstance(v, str)) and
            not isinstance(v, Callable)  # type: ignore
        ):
            self.df = self._ds._events[self._ds._events[k] == v]

        # Case where the specified value is a Collection but not a boolean mask.
        # Notice that a boolean mask is a special kind of Collection!
        elif (
            isinstance(v, Collection) and not
            self._is_column_mask(v, self._ds._events[k])
        ):
            self.df = self._ds._events[self._ds._events[k].isin(v)]

        # Case where the specified value is a boolean mask or a Callable that
        # when applied can be converted into one.
        else:
            if isinstance(v, Callable):  # type: ignore
                v = v(self._ds._events[k])

            if self._is_column_mask(v, self._ds._events[k]):
                self.df = self._ds._events[v.values]

        filterwarnings('always')  # Reactivate warnings.

    def expand_to_match_ds(
        self, dimension_matching_col: str, fill_value_col: str,
        fill_method: Optional[str] = None
    ) -> DataArray:
        """Expand a :py:attr:`_ds._events` column to match the shape of :py:attr:`_ds`.

        Given the column :py:attr:`dimension_matching_col` of the events
        :py:obj:`DataFrame` whose values form a subset of the values of a
        :py:obj:`Dataset` dimension or coordinate, this method will create a
        :py:obj:`DataArray` in such a way that its coordinates are the values of
        the aforementioned superset and the values are given by the column
        :py:attr:`fill_value_col` of the events :py:obj:`DataFrame`, filling in
        the emerging gaps as per :py:attr:`fill_method`.

        This subset-superset correspondance is a *mapping* (key-value pair) from
        a column of the events :py:obj:`DataFrame` (key) to a :py:obj:`Dataset`
        dimension or coordinate (value), and it must be previously specified in
        a dictionary during :py:meth:`load`. It is handled by the
        :py:meth:`df_ds_mapping` property.

        Call this method strictly after having called :py:meth:`load` with the
        :py:obj:`df_ds_mapping` argument.

        Tip: If you want to use the index of the events dataframe, and the index
        doesn’t have a name already, assign to :py:attr:`fill_value_col` the
        value 'event_index'.

        Args:
            dimension_matching_col: Events :py:obj:`DataFrame` column whose
                values form a subset of the values of some :py:obj:`Dataset`
                dimension or coordinate and will be expanded to match them. This
                argument uses a mapping from a column of the events
                :py:obj:`DataFrame` to a :py:obj:`Dataset` dimension or
                coordinate that must have already been specified upon calling
                :py:meth:`load`.
            fill_value_col: Events :py:obj:`DataFrame` column whose values fill
                the output array.
            fill_method: Method to be used to fill the gaps that emerge after
                expanding :py:attr:`dimension_matching_col`. The possible
                filling methods are the ones that
                :py:meth:`pd.DataFrame.reindex` supports. See `their official
                documentation
                <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reindex.html>`_
                for details.

        Returns:
            A :py:obj:`DataArray` created as specified above.

        Raises:
            KeyError: when either :py:attr:`dimension_matching_col` or
                :py:attr:`fill_value_col` is unrecognizable.

        Example:
            See :doc:`../../tutorials/sports_data/expand_to_match_ds`.

        """
        # Besides the index name, we also add event_index as a dummy to the list
        # of cols to handle the case where this method is called by another
        # method and therefore neither reset_index nor rename have been called
        # on self.df yet.
        df_cols_expanded = list(self.df) + [self.df.index.name, 'event_index']

        if (
            dimension_matching_col not in df_cols_expanded or
            fill_value_col not in df_cols_expanded
        ):
            raise KeyError(
                f'None of {[dimension_matching_col] + [fill_value_col]} '
                'are columns of the events DataFrame.'
            )

        return DataArray(
            self.df
            .reset_index()
            .rename(columns={'index': 'event_index'}, errors='ignore')
            .set_index(dimension_matching_col, drop=False)
            [fill_value_col]
            .reindex(
                self._ds[self.df_ds_mapping[dimension_matching_col]],
                method=fill_method
            )
        )

    def groupby_events(self, dimension_matching_col: str, array_to_group: str,
                       fill_method: Optional[str] = None) -> DataArrayGroupBy:
        """Group a data variable by the events in the :py:obj:`DataFrame`.

        This method uses a :py:obj:`DataArray` generated by
        :py:meth:`expand_to_match_ds` to group a :py:attr:`DataVariable` of the
        :py:obj:`Dataset`, resulting in a :py:obj:`GroupBy` object on which
        functions can be called.

        Call this method strictly after having called :py:meth:`load` with the
        :py:obj:`df_ds_mapping` argument.

        Args:
            dimension_matching_col: Events :py:obj:`DataFrame` column whose
                values form a subset of the values of some :py:obj:`Dataset`
                dimension or coordinate and will be expanded to match them. This
                argument uses a mapping from a column of the events
                :py:obj:`DataFrame` to a :py:obj:`Dataset` dimension or
                coordinate that must have already been specified upon calling
                :py:meth:`load`.
            array_to_group: :py:obj:`Dataset` data variable or coordinate to
                group.
            fill_method: Method to be used to fill the gaps that emerge after
                expanding :py:attr:`dimension_matching_col`. The possible
                filling methods are the ones that
                :py:meth:`pd.DataFrame.reindex` supports. Check `their official
                documentation
                <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reindex.html>`_
                for details.

        Returns:
            A :py:obj:`DataArrayGroupBy` (which is internally just like
            :py:obj:`GroupBy` from :py:mod:`pandas`) object.

        Raises:
            KeyError: when either :py:attr:`dimension_matching_col` or
                :py:attr:`fill_value_col` is unrecognizable.

        Example:
            See :doc:`../../tutorials/sports_data/groupby_events`.

        """
        if dimension_matching_col not in list(self.df_ds_mapping):
            raise KeyError(f'No match found for {dimension_matching_col} in '
                           'df_ds_mapping.')

        return (
            self._ds
            [array_to_group]
            .groupby(
                self.expand_to_match_ds(
                    dimension_matching_col,
                    self.df.index.name or 'event_index',
                    fill_method
                )
            )
        )

    def load(self, source: Union[DataFrame, Path, str],
             df_ds_mapping: Optional[dict] = None) -> Dataset:
        """Set the events :py:obj:`DataFrame` as an attribute of :py:attr:`_ds`.

        Depending on the source where the events are to be found, fetch and load
        them accordingly.

        This is the first method that should be called on a :py:obj:`Dataset`
        when using this API. The internal attribute it creates in
        :py:attr:`_ds` is :py:attr:`_events`.

        Optionally, :py:attr:`df_ds_mapping` can be specified. This dictionary
        consists of key-value pairs that establish a correspondance between an
        events :py:obj:`DataFrame` column and a :py:obj:`Dataset` dimension or
        coordinate, which is needed for some operations on events.

        To facilitate the task of referencing :py:attr:`_events`, we provide the
        *property* :py:meth:`df`. Assuming you have a :py:obj:`Dataset` called
        ``ds``, you may use it via ``ds.events.df``.

        Args:
            source: A :py:obj:`DataFrame` or :py:obj:`Path` specifying where the
                events are to be loaded from.

            df_ds_mapping: An optional dictionary where the keys are columns
                from :py:attr:`_ds.events` and the values are dimensions or
                coordinates from :py:attr:`_ds` thereby specifying a *mapping*
                between them.

        Returns:
            self._ds: the modified :py:obj:`Dataset` now including events.

        Raises:
            ValueError: on an invalid mapping.

        Example:
            See :doc:`../../tutorials/sports_data/loading`.

        """
        # A DataFrame is the ultimate way of representing the events.
        if isinstance(source, DataFrame):
            self._load_events_from_DataFrame(source)

        # Look for either a DataFrame or a Path from where to get the events.
        else:
            self._load_events_from_Path(Path(source))

        if df_ds_mapping:
            self.df_ds_mapping = df_ds_mapping

        return self._ds

    def sel(self, indexers: Mapping[str, Any] = None, method: str = None,
            tolerance: Number = None, drop: bool = False,
            **indexers_kwargs: Any) -> Dataset:
        """Perform a selection on :py:attr:`_ds` given specified constraints.

        This is a wrapper around :py:mod:`xr.Dataset.sel` that extends its
        functionality to support events handling.

        The arguments that match events :py:obj:`DataFrame` attributes are used
        to filter the events. Everything else is passed directly to
        :py:mod:`xr.Dataset.sel()`.

        Call this method by specifying constraints for both the
        :py:obj:`Dataset` dimensions and the events :py:obj:`DataFrame`
        attributes in a single dictionary.

        The values for the constraints may be of different types, and the
        behavior varies accordingly. Here's how it works:

        -   If the value is a *single value*, filter by it directly.

        -   If the value is an instance of :py:class:`Collection` (like a list),
            filter the events by them.

        -   If the value is a *boolean mask*, filter the :py:obj:`DataFrame` by
            it. In case the value is an instance of :py:class:`Collection` (like
            a lambda function), apply the function to the events
            :py:obj:`DataFrame` to obtain a mask first.

        Tip: If intended to be chained, call after having called :py:meth:`load`
        to ensure that the events are properly loaded.

        The arguments, return values and raised exceptions are the same as for
        :py:mod:`xr.Dataset.sel`, in order to stay true to the wrapper nature of
        this method. See the `official xarray documentation
        <http://xarray.pydata.org/en/stable/generated/xarray.Dataset.sel.html>`_
        for details.

        Example:
            See :doc:`../../tutorials/sports_data/selecting/index`.

        """
        if indexers is None:
            indexers = {}

        indexers_kwargs.update(indexers)
        # Constraints may refer to either Dataset dimensions or events attrs.
        constraints = indexers_kwargs

        # Events attributes, which may not exist.
        events = set(self.df.columns if '_events' in self._ds.attrs else {})

        # Calls xr.Dataset.sel with the method args as well as all constraints
        # that match Dataset dimensions.
        self._ds = self._ds.sel(
            {k: constraints[k] for k in set(constraints) - events},
            method=method, tolerance=tolerance, drop=drop
        )

        # Filters the events DataFrame by the appropriate constraints.
        for k, v in {
            k: constraints[k] for k in set(constraints) & events
        }.items():
            self._filter_events(k, v)

        # TODO: Here's a good place to drop "out-of-view" events.

        return self._ds
