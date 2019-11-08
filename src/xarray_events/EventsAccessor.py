"""Definition of the EventsAccessor class.

Define the EventsAccessor class with enough methods to act as a wrapper around
xarray extending its functionality to better support events data.
"""

from __future__ import annotations

import xarray as xr, pandas as pd

from typing import Union
from pathlib import Path

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
        """
        Arguments:
            ds (xr.Dataset): The Dataset to be accessed whose class-level
                functionality is to be extended.
        """
        self._ds = ds

    def load(self, source: Union[type(pd.DataFrame()), type(Path())]) -> self:
        """Set the events DataFrame as an attribute of _ds.

        Depending on the source where the events are to be found, fetch and load
        them accordingly.

        Arguments:
            source (DataFrame/PosixPath): A DataFrame or Path specifying where
                the events are to be loaded from.

        Returns:
            self, which contains the modified _ds now including events.

        Usage:
            First method that should be called on a Dataset upon using this API.

        Raises:
            AttributeError: if source is neither a DataFrame nor a Path.
        """

        # ** INTERNAL DEFINITIONS TO HANDLE THE LOADING **

        # if source is a DataFrame, assign it directly as an attribute of _ds
        def from_DataFrame(df: type(pd.DataFrame())) -> None:
            self._ds = self._ds.assign_attrs(_events = df)

        # various file formats supported
        # ! under construction !
        def from_csv() -> None:
            pass

        # if source is a Path, call the right handler depending on the extension
        def from_Path(p: type(Path())) -> None:
            if source.suffix == '.csv':
                from_csv()
            pass

        # ** MAIN CONTROL BLOCK **

        # a DataFrame is the ultimate way of representing the events
        if type(source) == type(pd.DataFrame()):
            from_DataFrame(source)

        # if a Path is given:
        #   1. fetch the data depending on the file extension
        #   2. convert it into a DataFrame
        elif type(source) == type(Path()):
            from_Path()

        else:
            raise AttributeError(
                'Unsupported source. Provide either a DataFrame or a Path.'
            )

        return self

    def sel(self, constraints: dict) -> self:
        """Perform a selection on _ds given a specified set of constraints.

        This is a wrapper around xr.Dataset.sel that extends its functionality
        to support events handling. Depending on the values of

            - the specified constraints (c)
            - the Dataset dimensions (d)
            - the events DataFrame attributes/columns (e)

        the following functionality is supported:

        1. c and d match exactly: xr.Dataset.sel is called with no modifications

        2. c and e match exactly: _ds stays the same but _ds.events is filtered

        3. c matches both d and e: using the appropriate constraints,
            3-1. xr.Dataset.sel is used on _ds
            3-2. _ds.events is filtered

        Arguments:
            constraints (dict): A dictionary specifying values for either
                Dataset dimensions or events attributes by which to filter _ds.

        Returns:
            self, which contains a modified _ds having applied all constraints.

        Usage:
            Call strictly after having called load to ensure that the events
            are stored correctly.

        Raises:
            ValueError: if some unrecognizable constraint is given.
        """

        # if no constraint is given, perform no selection
        if not constraints:
            return self

        c = set(constraints)                        # specified constraints
        d = set(self._ds.dims)                      # Dataset dimensions
        e = set(self._ds.attrs['_events'].columns)  # events attributes

        # if dimensions and constraints match exactly
        if d == c:
            self._ds = self._ds.sel(constraints)
            return self

        # if events attributes and constraints match exactly, filter the events
        # DataFrame by the specified constraints
        if e == c:

            for k,v in constraints.items():

                if type(v) == type([]):
                    self._ds.attrs['_events'] = self._ds._events[
                        self._ds._events[k].isin(v)
                    ]

                else:
                    self._ds.attrs['_events'] = self._ds._events[
                        self._ds._events[k] == v
                    ]

            return self

        # if some unrecognized constraint was given
        # If a given constraint lies outside the union of the Dataset dimensions
        # and the events attributes then it is unrecognizable.
        if not (c <= (d | e)):
            raise ValueError

        # At this point we know that
        #   1. some constraints correspond to Dataset dimensions, and
        #   2. some to events attributes.
        # Hence, we just need to call filter both the Dataset and the events
        # DataFrame with the appropriate values.

        # use xr.Dataset.sel to filter the Dataset with the constraints that
        # match the Dataset dimensions
        self._ds = self._ds.sel({k:constraints[k] for k in (c & d)})

        # filter _events with constraints matching events attributes
        for k,v in {k:constraints[k] for k in (c & e)}.items():

            if type(v) == type([]):
                self._ds.attrs['_events'] = self._ds._events[
                    self._ds._events[k].isin(v)
                ]

            else:
                self._ds.attrs['_events'] = self._ds._events[
                    self._ds._events[k] == v
                ]

        return self
