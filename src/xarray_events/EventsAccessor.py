"""Definition of the EventsAccessor class.

Define the EventsAccessor class with enough methods to act as a wrapper around
xarray extending its functionality to better support events data.

"""
from __future__ import annotations
from typing import Union
from pathlib import Path
from collections.abc import Collection, Callable
from typing import Optional
import warnings

import xarray as xr
import pandas as pd

@xr.register_dataset_accessor('events')
class EventsAccessor:
    """xarray accessor with extended events-handling functionality.

    An xarray accessor that extends its functionality to handle events in a
    high-level way. This API makes it easy to load events into an existing
    Dataset from a variety of sources and perform selections on the events
    satisfying a set of specified constraints.

    Attributes:
        _ds (xr.Dataset): The Dataset to be accessed whose class-level
            functionality is to be extended.

    """
    def __init__(self, ds) -> None:
        self._ds = ds

    @property
    def df(self) -> pd.DataFrame:
        """Get or set the events DataFrame into an attribute of the Dataset.

        Getting the events DataFrame when it doesn't exist raises an exception.

        Setting the events DataFrame when it apparently already exists raises a
        warning.

        """
        try:
            return self._ds.attrs['_events']
        except KeyError:
            raise TypeError('Events not yet loaded')

    @df.setter
    def df(self, events: pd.DataFrame) -> None:
        if '_events' in self._ds.attrs:
            warnings.warn(
                'Attempting to load events despite _events being already an '
                'attribute of the Dataset.'
            )
        self._ds.attrs['_events'] = events

    @property
    def df_ds_mapping(self) -> pd.DataFrame:
        """Get or set a df-ds col-dim mapping into an attribute of the Dataset.

        Getting the mapping dict when it doesn't exist raises an exception.

        Setting the mapping dict when it apparently already exists raises a
        warning.

        """
        try:
            return self._ds.attrs['_df_ds_mapping']
        except KeyError:
            raise TypeError('Mapping not yet loaded')

    @df_ds_mapping.setter
    def df_ds_mapping(self, mapping: pd.DataFrame) -> None:
        if '_df_ds_mapping' in self._ds.attrs:
            warnings.warn(
                'Attempting to load the df-ds mapping despite _df_ds_mapping '
                'being already an attribute of the Dataset.'
            )
        self._ds.attrs['_df_ds_mapping'] = mapping

    def _load_events_from_DataFrame(self, df: pd.DataFrame) -> None:
        # If source is a DataFrame, assign it directly as an attribute of _ds.
        self._ds = self._ds.assign_attrs(_events = df)

    def _load_events_from_csv() -> None:
        pass

    def _load_events_from_Path(self, p: Path) -> None:
        # If source is a Path, call the right handler depending on the extension
        if source.suffix == '.csv':
            self._load_events_from_csv()
        pass

    def _is_column_mask(self, val: Collection, col: pd.Series) -> bool:
        # Checks whether a Collection is a boolean mask of a Dataframe column.
        return len(val) == len(col) and all(type(x) == bool for x in val)

    def _filter_events(self, k: str, v) -> None:
        # we need to disable the warnings that will be thrown due to calling
        # the setter df since they aren't meaningful in this case
        warnings.filterwarnings('ignore')

        # case where the specified value is a "single value", which is anything
        # that's neither a Collection nor a Callable
        if not isinstance(v, Collection) and not isinstance(v, Callable):
            self.df = self._ds._events[self._ds._events[k] == v]

        # case where the specified value is a Collection but not a boolean mask
        # notice that a boolean mask is a special kind of Collection
        elif (
            isinstance(v, Collection)
            and not self._is_column_mask(v, self._ds._events[k])
        ):
            self.df = self._ds._events[self._ds._events[k].isin(v)]

        # case where the specified value is a boolean mask or a Callable that
        # when applied can be converted into one
        else:
            if isinstance(v, Callable):
                v = v(self._ds._events[k])

            if self._is_column_mask(v, self._ds._events[k]):
                self.df = self._ds._events[v.values]

        # re-activate warnings
        warnings.filterwarnings('always')

    def get_group_array(self, dimension_matching_col: str, fill_value_col: str,
                        fill_method: Optional[str] = None) -> xr.DataArray:
        """Expand a _ds._events column to match the shape of _ds.

        Given a column of the Events DataFrame (dimension_matching_col) whose
        values form a subset of the values of a Dataset dimension or coordinate,
        this method will create a DataArray in such a way that its coordinates
        are the values of the aforementioned superset and the values are given
        by another column of the Events DataFrame (fill_value_col), filling in
        the emerging gaps as per fill_method.

        This subset-superset correspondance is a mapping (key-value pair) from a
        column of the Events DataFrame (key) to a Dataset dimension or
        coordinate (value), and it must be previously specified in a dictionary
        during load.

        Usage:
            Call this method strictly after having called load specifying the
            matching between dimension_col and some Dataset DataVariable or
            Coordinate.

        Arguments:
            dimension_matching_col (str): Events DataFrame column whose values
            form a subset of the values of some Dataset DataVariable or
            Coordinate and will be expanded to match them. This argument uses a
            mapping from events DataFrame column to Dataset DataVariable or
            Coordinate that must have already been specified during load.

            fill_value_col (str): Events DataFrame column whose values fill the
            output array.

            fill_method (str, optional): Method to be used to fill the gaps that
            emerge after expanding dimension_matching_col. The possible filling
            methods are the ones that pd.DataFrame.reindex supports. Check their
            official documentation for details.

        Returns:
            A DataArray created as specified above.

        Raises:
            KeyError: when either dimension_matching_col or fill_value_col is
            unrecognizable.

        Example:
            .!.under construction.!.

        """
        # besides the index name, we also add event_index as a dummy to the list
        # of cols to handle the case where this method is called by another
        # method and therefore neither reset_index nor rename have been called
        # on self.df yet
        df_cols_expanded = list(self.df) + [self.df.index.name, 'event_index']

        if (dimension_matching_col not in df_cols_expanded or
            fill_value_col not in df_cols_expanded):
            raise KeyError(
                f'None of {[dimension_matching_col] + [fill_value_col]} '
                'are columns of the events DataFrame.'
            )

        return xr.DataArray(
            self.df
            .reset_index()
            .rename(columns = {'index': 'event_index'}, errors = 'ignore')
            .set_index(dimension_matching_col, drop = False)
            [fill_value_col]
            .reindex(
                self._ds[self.df_ds_mapping[dimension_matching_col]],
                method = fill_method
            )
        )

    def groupby_events(self, dimension_matching_col: str, array_to_group: str,
                       fill_method: Optional[str] = None):
        """Group a DataVariable by an events DataFrame column.

        This method simply calls get_group_array to generate a group by which to
        group a DataVariable of the Dataset.

        Usage:
            Call this method strictly after having called load specifying the
            matching between dimension_col and some Dataset DataVariable or
            Coordinate.

        Arguments:
            dimension_matching_col (str): Events DataFrame column whose values
            form a subset of the values of the coordinates of array_to_group.
            This argument uses a mapping from events DataFrame column to Dataset
            DataVariable or Coordinate that must have already been specified
            during load.

            array_to_group (str): Dataset DataVariable or Coordinate to group.

            fill_method (str, optional): Method to be used to fill the gaps that
            emerge after expanding dimension_matching_col. The possible filling
            methods are the ones that pd.DataFrame.reindex supports. Check their
            official documentation for details.

        Returns:
            A DataArray created as specified above.

        Raises:
            KeyError: when either dimension_matching_col or fill_value_col is
            unrecognizable.

        Example:
            .!.under construction.!.

        """
        if dimension_matching_col not in list(self.df):
            raise KeyError(f'{dimension_matching_col} not a column of the '
                           'events DataFrame.')

        if array_to_group not in list(self._ds):
            raise KeyError(f'{array_to_group} not a DataVariable of the '
                           'Dataset.')

        return (
            self._ds
            [array_to_group]
            .groupby(
                self.get_group_array(
                    dimension_matching_col,
                    self.df.index.name or 'event_index',
                    fill_method
                )
            )
        )

    def load(self, source: Union[pd.DataFrame, Path, str],
             df_ds_mapping: dict = None) -> xr.Dataset:
        """Set the events DataFrame as an attribute of _ds.

        Depending on the source where the events are to be found, fetch and load
        them accordingly.

        Usage:
            First method that should be called on a Dataset upon using this API.

        Arguments:
            source (DataFrame/PosixPath/str): A DataFrame or Path specifying
                where the events are to be loaded from.

            df_ds_mapping (dict, optional): An optional dictionary where the
            keys are columns from _ds.events and the values are dimensions or
            coordinates from _ds thereby specifying a mapping between them.

        Returns:
            self._ds: the modified Dataset now including events.

        Raises:
            ValueError: on an invalid mapping.

        """
        # a DataFrame is the ultimate way of representing the events
        if isinstance(source, pd.DataFrame):
            self._load_events_from_DataFrame(source)

        # look for either a DataFrame or a Path from where to get the events
        else:
            self._load_events_from_Path(Path(source))

        if df_ds_mapping:
            df_given = set(df_ds_mapping)
            df_real = set(self.df)

            ds_given = set(df_ds_mapping.values())
            ds_real = set(self._ds) | set(self._ds.coords)

            if not df_given <= df_real:
                raise ValueError(
                    f'Invalid mapping. None of {df_given - df_real} are event '
                    'DataFrame columns.')

            if not ds_given <= ds_real:
                raise ValueError(
                    f'Invalid mapping. None of {ds_given - ds_real} are '
                    'Dataset dimensions or coordinates.')

            self.df_ds_mapping = df_ds_mapping

        return self._ds

    def sel(self, indexers: Mapping[Hashable, Any] = None, method: str = None,
            tolerance: numbers.Number = None, drop: bool = False,
            **indexers_kwargs: Any) -> xr.Dataset:
        """Perform a selection on _ds given a specified set of constraints.

        This is a wrapper around xr.Dataset.sel that extends its functionality
        to support events handling.

        The arguments that match events DataFrame attributes are used to filter
        the events. Everything else is passed directly to xr.Dataset.sel.

        Usage:
            Call by specifying constraints for both the Dataset dimensions and
            the events DataFrame attributes in a single dictionary.

        The values for the constraints may be of different types, and the
        behavior varies accordingly. Here's how it works:

        - If the value is a single value, filter by it directly.

        - If the value is a Collection (like a list), filter the events by them.

        - If the value is a boolean mask, filter the DataFrame by it. In case
        the value is Callable (like a lambda function), apply the function to
        the events DataFrame to obtain a mask first.

        Tip: If intended to be chained, call after having called load to ensure
        that the events are properly loaded.

        The arguments, return values and raised exceptions are the same as for
        xr.Dataset.sel, in order to stay true to the wrapper nature of this
        method. See the official xarray documentation for details.

        """
        # constraints may refer to either Dataset dimensions or events attrs
        constraints = {**indexers, **indexers_kwargs}

        # events attributes, which may not exist
        events = set(self.df.columns if '_events' in self._ds.attrs else {})

        # call xr.Dataset.sel with the method args as well as all constraints
        # that match Dataset dimensions
        self._ds = self._ds.sel(
            {k: constraints[k] for k in set(constraints) - events},
            method = method, tolerance = tolerance, drop = drop
        )

        # filter the events DataFrame by the appropriate constraints
        for k,v in {k:constraints[k] for k in set(constraints) & events}.items():
            self._filter_events(k,v)

        # TODO: Here's a good place to drop "out-of-view" events.

        return self._ds
