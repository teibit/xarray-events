"""Unit tests for the EventsAccessor class.

Test the behavior of each method of the EventsAccessor class, in a separate
class each, to ensure robustness while the code grows.

    Usage: Assuming the current directory is the main one,

        $ pytest -q tests/test.py -rpf

        will run all tests and provide a summary of the passed/failed ones.

"""
from ..src.xarray_events.EventsAccessor import EventsAccessor
from pandas.util.testing import assert_frame_equal
from xarray.testing import assert_identical

import pytest
import xarray as xr
import pandas as pd

class Test_load:
    def test_load_events_from_DataFrame(self) -> None:
        """
        When load is called with a DataFrame as an argument, ensure that it adds
        the attribute _events to the Dataset with the provided value.

        """
        events = pd.DataFrame(data = [[11,12],[21,22]], columns = ['ea1','ea2'])

        assert_frame_equal(
            events,
            xr.Dataset()
                .events.load(events)
                .events._ds._events
        )

    # ! under construction !
    class Test_load_events_from_Path:
        # ! under construction !
        def test_load_events_from_csv(self) -> None:
            assert False

class Test_sel:
    def test_args_match_only_dims(self) -> None:
        """
        When the dictionary of constraints refers exclusively to dimensions
        of the Dataset, ensure that the selection result is the same
        as the one already provided by default on xarray.

        """
        ds = xr.Dataset({'dv1': (['d1'],[0])}, {'d1': ['coord1']})

        selection = {'d1': 'coord1'}

        assert_identical(ds.sel(selection), ds.events.sel(selection))

    def test_args_match_only_events(self) -> None:
        """
        When the dictionary of constraints refers exclusively to event attrs,
        ensure that the selection result filters the events DataFrame with the
        matching attrs and the Dataset stays the same.

        """
        events = pd.DataFrame(
            data = [[11,12],[21,22]],
            columns = ['ea1','ea2']
        )

        ds = xr.Dataset(
            {'dv1': (['d1'],[1,2])},
            {'d1': ['coord1','coord2']},
            {'_events': events}
        )

        result = ds
        result.attrs['_events'] = result._events[result._events['ea1'] == 11]

        assert result == ds.events.sel({'ea1': 11})

    def test_args_match_both_dims_events(self) -> None:
        """
        When the dictionary of constraints refers to both dimensions of the
        Dataset and attributes of the events DataFrame, ensure that the
        selection result is the same as if we:
            1. make a selection on the dimensions with the matching coords
            2. filter the events DataFrame with the matching attrs

        """
        events = pd.DataFrame(
            data = [[11,12],[21,22]],
            columns = ['ea1','ea2']
        )

        ds = xr.Dataset(
            {'dv1': (['d1'],[1,2])},
            {'d1': ['coord1','coord2']},
            {'_events': events}
        )

        result = ds.sel({'d1': 'coord1'})
        result.attrs['_events'] = result._events[result._events['ea1'] == 11]

        # v1 == v2 for Dataset does element-wise comparisons
        assert result == ds.events.sel({'d1': 'coord1', 'ea1': 11})

    def test_args_match_both_dims_args(self) -> None:
        """
        When the dictionary of constraints refers to both dimensions of the
        Dataset and arguments of the method xr.Dataset.sel, ensure that the
        selection result is the same as the one already provided by default on
        xarray.

        """
        ds = xr.Dataset({'dv1': (['d1'],[0])}, {'d1': ['coord1']})

        selection = {'d1': 'coord1'}

        assert_identical(
            ds.sel(selection, drop = True),
            ds.events.sel(selection, drop = True)
        )

    def test_args_match_dims_args_events(self) -> None:
        """
        When the dictionary of constraints refers to Dataset dimensions, method
        args and attributes of the events DataFrame, ensure that the selection
            1. calls xr.Dataset.sel with
                1-1. the matching coords
                1-2. the matching method args
            2. filters the events DataFrame with the matching attrs

        """
        events = pd.DataFrame(
            data = [[11,12],[21,22]],
            columns = ['ea1','ea2']
        )

        ds = xr.Dataset(
            {'dv1': (['d1'],[1,2])},
            {'d1': ['coord1','coord2']},
            {'_events': events}
        )

        result = ds.sel({'d1': 'coord1'}, method = 'pad')
        result.attrs['_events'] = result._events[result._events['ea1'] == 11]

        assert result == ds.events.sel({'d1':'coord1','ea1':11}, method = 'pad')

    def test_constraint_is_Collection(self) -> None:
        """
        When the values of the dictionary of constraints refer to a Collection,
        ensure that the events are properly filtered by all of these values.

        For this test, the constraints match only event DataFrame attrs.

        """
        events = pd.DataFrame(data = [[11,12],[21,22]], columns = ['ea1','ea2'])

        assert_frame_equal(
            xr.Dataset()
                .events.load(events)
                .events.sel({'ea1': [11]})
                .events._ds._events,
            pd.DataFrame(data = [[11,12]], columns = ['ea1','ea2'])
        )

    def test_constraint_is_Callable(self) -> None:
        """
        When the values of the dictionary of constraints refer to a Callable,
        ensure that the events are properly filtered by this.

        For this test, the constraints match only event DataFrame attrs.

        """
        events = pd.DataFrame(data = [[11,12],[21,22]], columns = ['ea1','ea2'])

        assert_frame_equal(
            xr.Dataset()
                .events.load(events)
                .events.sel({'ea1': lambda x: x == 11})
                .events._ds._events,
            pd.DataFrame(data = [[11,12]], columns = ['ea1','ea2'])
        )
