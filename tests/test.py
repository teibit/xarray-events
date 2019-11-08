"""Unit tests for the EventsAccessor class.

Test the behavior of each method of the EventsAccessor class, in a separate
class each, to ensure robustness while the code grows.

    Usage: Assuming the current directory is release,

        $ pytest -q tests/test.py -rpf

        will run all tests and provide a summary of the passed/failed ones.
"""

from ..src.xarray_events.EventsAccessor import EventsAccessor

import pytest, xarray as xr, pandas as pd

class Test_load:

    def test_from_DataFrame(self) -> None:
        """
        When load is called with a DataFrame as an argument, ensure that it adds
        the attribute _events to the Dataset with the provided value.
        """

        events = pd.DataFrame(data = [[11,12],[21,22]], columns = ['ea1','ea2'])

        assert xr.Dataset().events.load(events)._ds._events.equals(events)

    # ! under construction !
    class Test_load_from_Path:

        # ! under construction !
        def test_from_csv(self) -> None:
            assert False

class Test_sel:

    def test_constraints_match_only_dims(self) -> None:
        """
        When the dictionary of constraints refers exclusively to dimensions
        of the Dataset, ensure that the selection result is the same
        as the one already provided by default on xarray.
        """

        ds = xr.Dataset(
            {'dv1': (['d1'],[0])},
            {'d1': ['coord1']},
            {'_events': pd.DataFrame()}
        )

        result = ds.sel({'d1': 'coord1'})

        assert result.equals(ds.events.sel({'d1': 'coord1'})._ds)

    def test_constraints_match_both_dims_events(self) -> None:
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

        assert result.equals(ds.events.sel({'d1': 'coord1', 'ea1': 11})._ds)

    def test_constraints_match_neither_dims_events(self) -> None:
        """
        When the dictionary of constraints refers to neither dimensions of the
        Dataset nor attributes of the events DataFrame, ensure that a ValueError
        exception is raised.
        """

        ds = xr.Dataset(
            coords = {'d1': ['coord1']},
            attrs = {'_events': pd.DataFrame(columns = ['ea1'])}
        )

        with pytest.raises(ValueError):
            ds.events.sel({'x': 0})
