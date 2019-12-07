"""Definition of the EventsAccessor class.

Define the EventsAccessor class with enough methods to act as a wrapper around
xarray extending its functionality to better support events data.

"""
from __future__ import annotations
from typing import Union
from pathlib import Path
from collections.abc import Collection, Callable

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
        # case where the specified value is a "single value", which is anything
        # that's neither a Collection nor a Callable
        if not isinstance(v, Collection) and not isinstance(v, Callable):
            self._ds.attrs['_events'] = self._ds._events[
                self._ds._events[k] == v
            ]

        # case where the specified value is a Collection but not a boolean mask
        # notice that a boolean mask is a special kind of Collection
        elif (
            isinstance(v, Collection)
            and not self._is_column_mask(v, self._ds._events[k])
        ):
            self._ds.attrs['_events'] = self._ds._events[
                self._ds._events[k].isin(v)
            ]

        # case where the specified value is a boolean mask or a Callable that
        # when applied can be converted into one
        else:
            if isinstance(v, Callable):
                v = v(self._ds._events[k])

            if self._is_column_mask(v, self._ds._events[k]):
                self._ds.attrs['_events'] = self._ds._events[v.values]

    def load(self, source: Union[pd.DataFrame, Path, str]) -> xr.Dataset:
        """Set the events DataFrame as an attribute of _ds.

        Depending on the source where the events are to be found, fetch and load
        them accordingly.

        Usage:
            First method that should be called on a Dataset upon using this API.

        Arguments:
            source (DataFrame/PosixPath/str): A DataFrame or Path specifying
                where the events are to be loaded from.

        Returns:
            self, which contains the modified _ds now including events.

        Raises:
            TypeError: if source is neither a DataFrame nor a Path.

        """
        # a DataFrame is the ultimate way of representing the events
        if isinstance(source, pd.DataFrame):
            self._load_events_from_DataFrame(source)

        # if a Path is given:
        #   1. fetch the data depending on the file extension
        #   2. convert it into a DataFrame
        elif isinstance(source, Path):
            self._load_events_from_Path(source)

        # if a string is given, and assuming it corresponds with a path:
        #   1. convert it into a Path
        #   2. handle it accordingly
        elif isinstance(source, str):
            self._load_events_from_Path(Path(source))

        else:
            raise TypeError(
                f'Unexpected type {type(source).__name__!r}. Expected Dataframe'
                ', str or Path instead.'
            )

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

        d = set(self._ds.dims) # Dataset dimensions

        # events attributes, which may not exist
        e = set(self._ds.attrs['_events'].columns if self._ds.attrs else {})

        # call xr.Dataset.sel with the method args as well as all constraints
        # that match Dataset dimensions
        self._ds = self._ds.sel(
            {k:constraints[k] for k in set(constraints) & d},
            method, tolerance, drop
        )

        # filter the events DataFrame by the appropriate constraints
        for k,v in {k:constraints[k] for k in set(constraints) & e}.items():
            self._filter_events(k,v)

        # TODO: Here's a good place to drop "out-of-view" events.

        return self._ds
