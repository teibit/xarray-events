"""Unit tests for the EventsAccessor class.

Test the behavior of each method of the EventsAccessor class, in a separate
class each, to ensure robustness while the code grows.

    Usage: Assuming the current directory is the main one,

        $ pytest -q tests/test.py -rpPf

        will run all tests and provide a summary of the passed/failed ones,
        along with any captured console output.

"""
import xarray_events
from pandas.util.testing import assert_frame_equal
from xarray.testing import assert_identical
from xarray.testing import assert_equal
from typing import Any, Hashable, Mapping, Optional, Union

import pytest
import xarray as xr
import pandas as pd
import numpy as np


class Test_load:
    """Test the method load from EventsAccessor."""

    def test_load_events_from_DataFrame(self) -> None:
        """Use a DataFrame.

        When load is called with a DataFrame as an argument, ensure that it adds
        the attribute _events to the Dataset with the provided value.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        assert_frame_equal(
            ds
            .events.load(events)
            .events._ds._events,
            events
        )

    def test_load_mapping_wrong_df(self) -> None:
        """Use an invalid DataFrame.

        When the provided df_ds_mapping contains invalid event DataFrame
        columns, ensure that a ValueError is raised.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 100],
            'end_frame': [200, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        df_ds_mapping = {'starting_frame': 'frame', 'finishing_frame': 'frame'}

        with pytest.raises(ValueError):
            ds.events.load(events, df_ds_mapping)

    def test_load_valid_mapping(self) -> None:
        """Use a correct mapping.

        When df_ds_mapping is correctly provided, ensure that it is correctly
        stored.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 100],
            'end_frame': [200, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        result = ds.assign_attrs(_events=events, _df_ds_mapping=df_ds_mapping)

        assert_identical(ds.events.load(events, df_ds_mapping), result)

    def test_load_mapping_wrong_ds(self) -> None:
        """Use an invalid Dataset.

        When the provided df_ds_mapping contains invalid Dataset dimensions or
        coordinates, ensure that a ValueError is raised.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 100],
            'end_frame': [200, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'f', 'end_frame': 'f'}

        with pytest.raises(ValueError):
            ds.events.load(events, df_ds_mapping)

    # ! under construction !
    class Test_load_events_from_Path:
        """aaa.
        When ..., ensure that ...

        """
        def test_load_events_from_csv(self) -> None:
            """aaa.
            When ..., ensure that ...

            """
            assert True


class Test_sel:
    """Test the method sel from EventsAccessor."""

    def test_args_match_nothing(self) -> None:
        """Use invalid selection value.

        When an invalid value is provided for selection, ensure that a
        ValueError is raised.

        """
        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        selection = {'coords': 'x'}

        with pytest.raises(ValueError):
            ds.events.sel(selection)

    def test_args_ok_dims_wrong_events(self) -> None:
        """Use an invalid events DataFrame attribute.

        When the dictionary of constraints refers to correct dimensions or
        coordinates of the Dataset but incorrect events DataFrame attribute,
        ensure that a ValueError is thrown.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        selection = {'cartesian_coords': 'x', 'starting_frame': 1}

        with pytest.raises(ValueError):
            (
                ds
                .events.load(events)
                .events.sel(selection)
            )

    def test_args_wrong_dims_ok_events(self) -> None:
        """Use an invalid Dataset dimension or coordinate.

        When the dictionary of constraints refers to incorrect dimensions or
        coordinates of the Dataset but correct events DataFrame attribute,
        ensure that a ValueError is thrown.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        selection = {'coords': 'x', 'start_frame': 1}

        with pytest.raises(ValueError):
            (
                ds
                .events.load(events)
                .events.sel(selection)
            )

    def test_args_match_only_dims(self) -> None:
        """Match exclusively a Dataset dimension or coordinate.

        When the dictionary of constraints refers exclusively to dimensions or
        coordinates of the Dataset, ensure that the selection result is the same
        as the one already provided by default on xarray.

        """
        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        selection: Mapping[Hashable, Any] = {'cartesian_coords': 'x'}

        assert_identical(ds.sel(selection), ds.events.sel(selection))

    def test_args_match_only_events(self) -> None:
        """Match exclusively an events DataFrame attribute.

        When the dictionary of constraints refers exclusively to event attrs,
        ensure that the selection result filters the events DataFrame with the
        matching attrs and the Dataset stays the same.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25, '_events': events}
        )

        selection = {'start_frame': 1}

        # check that the events DataFrames are the same
        assert_frame_equal(
            ds
            .events.sel(selection)
            .events._ds._events,
            events[events['start_frame'] == 1]
        )

        # check that the Datasets are the same
        assert_equal(ds.events.sel(selection), ds)

    def test_args_match_both_dims_events(self) -> None:
        """Match Dataset dimension/coordinate and events DataFrame attribute.

        When the dictionary of constraints refers to both dimensions or
        coordinates of the Dataset and attributes of the events DataFrame,
        ensure that the selection result is the same as if we:
            1. make a selection on the dimensions with the matching coords
            2. filter the events DataFrame with the matching attrs

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        selection = {'cartesian_coords': 'x', 'start_frame': 1}

        actual_result = (
            ds
            .events.load(events)
            .events.sel(selection)
        )

        expected_result = (
            ds
            .sel(cartesian_coords='x')
            .assign_attrs({'_events': events[events['start_frame'] == 1]})
        )

        # Ensure that the Datasets are equal disregarding attributes.
        assert_equal(actual_result, expected_result)

        # Ensure that the Datasets' _events attribute is equal.
        assert_frame_equal(actual_result.events.df, expected_result._events)

    def test_single_arg_matches_both_dims_events(self) -> None:
        """Match Dataset dimension/coordinate and events DataFrame attribute.

        When the dictionary of constraints refers to both a dimension or
        coordinate of the Dataset and an attribute of the events DataFrame,
        ensure that the selection result returns a Dataset in which the
        constraint was correctly enforced in both the Dataset dimension or
        coordinate and also in the DataFrame.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['start_frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={
                'start_frame': np.arange(1, 251),
                'cartesian_coords': ['x', 'y']
            },
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        selection = {'start_frame': 1}

        actual_result = (
            ds
            .events.load(events)
            .events.sel(selection)
        )

        expected_result = (
            ds
            .sel(start_frame=1)
            .assign_attrs({'_events': events[events['start_frame'] == 1]})
        )

        # Ensure that the Datasets are equal disregarding attributes.
        assert_equal(actual_result, expected_result)

        # Ensure that the Datasets' _events attribute is equal.
        assert_frame_equal(actual_result.events.df, expected_result._events)

    def test_args_match_both_dims_args(self) -> None:
        """Match both a Dataset dimension or coordinate and a method argument.

        When the dictionary of constraints refers to both dimensions or
        coordinates of the Dataset and arguments of the method xr.Dataset.sel,
        ensure that the selection result is the same as the one already provided
        by default on xarray.

        """
        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        selection: Mapping[Hashable, Any] = {'cartesian_coords': 'x'}

        assert_identical(
            ds.events.sel(selection, drop=True),
            ds.sel(selection, drop=True)
        )

    def test_args_match_dims_args_events(self) -> None:
        """Match every possible thing.

        When the dictionary of constraints refers to Dataset dimensions or
        coordinates, method args and attributes of the events DataFrame, ensure
        that the selection
            1. calls xr.Dataset.sel with
                1-1. the matching coords
                1-2. the matching method args
            2. filters the events DataFrame with the matching attrs

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        actual_result = (
            ds
            .events.load(events)
            .events.sel(
                {'cartesian_coords': 'x', 'start_frame': 1}, drop=True
            )
        )

        expected_result = (
            ds
            .sel(cartesian_coords='x', drop=True)
            .assign_attrs({'_events': events[events['start_frame'] == 1]})
        )

        # Ensure that the Datasets are equal disregarding attributes.
        assert_equal(actual_result, expected_result)

        # Ensure that the Datasets' _events attribute is equal.
        assert_frame_equal(actual_result.events.df, expected_result._events)

    def test_constraint_is_Collection(self) -> None:
        """Specify a Collection as a constraint value.

        When the values of the dictionary of constraints refer to a Collection,
        ensure that the events are properly filtered by all of these values.

        For this test, the constraints match only event DataFrame attrs.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25, '_events': events}
        )

        selection = {'start_frame': [1]}

        # check that the events DataFrames are the same
        assert_frame_equal(
            ds
            .events.sel(selection)
            .events._ds._events,
            events[events['start_frame'] == 1]
        )

        # check that the Datasets are the same
        assert_equal(ds.events.sel(selection), ds)

    def test_constraint_is_Callable(self) -> None:
        """Specify a Callable as a constraint value.

        When the values of the dictionary of constraints refer to a Callable,
        ensure that the events are properly filtered by this.

        For this test, the constraints match only event DataFrame attrs.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25, '_events': events}
        )

        selection = {'start_frame': lambda x: x == 1}

        # check that the events DataFrames are the same
        assert_frame_equal(
            ds
            .events.sel(selection)
            .events._ds._events,
            events[events['start_frame'] == 1]
        )

        # check that the Datasets are the same
        assert_equal(ds.events.sel(selection), ds)


class Test_expand_to_match_ds:
    """Test the method expand_to_match_ds from EventsAccessor."""

    def test_no_df_ds_mapping_given_to_load(self):
        """Use without having specified df_ds_mapping.

        When no df_ds_mapping is given to load before calling
        expand_to_match_ds, ensure that a TypeError is raised.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        with pytest.raises(TypeError):
            (
                ds
                .events.load(events)
                .events.expand_to_match_ds('end_frame', 'event_index', 'bfill')
            )

    def test_no_fill_method(self) -> None:
        """Use no fill method.

        When no fill_method is given, ensure that the resulting DataArray shows
        intact values from the events DataFrame and lots of nans as expected.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        result = xr.DataArray(
            data=[0] + [np.nan] * 173 + [1] + [np.nan] * 75,
            coords={'frame': np.arange(1, 251)},
            dims=['frame'],
            name='event_index'
        )

        assert_identical(
            ds
            .events.load(events, df_ds_mapping)
            .events.expand_to_match_ds('start_frame', 'event_index'),
            result
        )

    def test_custom_index_mapping_given_ffill(self) -> None:
        """Use a custom index name and the filling method ffill.

        When the filling method is 'ffill', ensure that the resulting DataArray
        is filled appropriately.

        In this scenario, changing this filling method changes the output
        dramatically without introducing nans.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        events.index.name = 'custom_index_name'

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        result = xr.DataArray(
            data=[0] * 174 + [1] * 76,
            coords={'frame': np.arange(1, 251)},
            dims=['frame'],
            name='custom_index_name'
        )

        assert_identical(
            ds
            .events.load(events, df_ds_mapping)
            .events.expand_to_match_ds(
                'start_frame', 'custom_index_name', 'ffill'
            ),
            result
        )

    def test_default_index_mapping_given_nearest(self) -> None:
        """Use filling method nearest.

        When the filling method is 'nearest', ensure that the resulting
        DataArray is filled appropriately.

        This filling method can be very useful in situations where there are
        evenly-spaced gaps between the events. In fact, even if the gaps aren't
        evenly-spaced and depending on the data, this filling method *might* be
        useful too.

        In this example, we're grouping by start_frame. Given that they are 1
        and 200, this method will fill 1 up until a point where 200 would also
        fill backwards and both would be evenly distributed. This is convenient
        since the first event finishes at frame 100, so it matches and the
        behavior is correct.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 200],
            'end_frame': [100, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        result = xr.DataArray(
            data=[0] * 100 + [1] * 150,
            coords={'frame': np.arange(1, 251)},
            dims=['frame'],
            name='event_index'
        )

        assert_identical(
            ds
            .events.load(events, df_ds_mapping)
            .events.expand_to_match_ds('start_frame', 'event_index', 'nearest'),
            result
        )

    def test_dimension_matching_col_invalid(self) -> None:
        """Use an invalid dimension_matching_col.

        When dimension_matching_col isn't a valid events DataFrame column,
        ensure that a KeyError is raised.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        with pytest.raises(KeyError):
            (
                ds
                .events.load(events, df_ds_mapping)
                .events.expand_to_match_ds('starting_frame', 'event_index')
            )

    def test_fill_value_col_invalid(self) -> None:
        """Use an invalid fill_value_col.

        When fill_value_col isn't a valid events DataFrame column, ensure that a
        KeyError is raised.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        with pytest.raises(KeyError):
            (
                ds
                .events.load(events, df_ds_mapping)
                .events.expand_to_match_ds('start_frame', 'event_id')
            )


class Test_groupby_events:
    """Test the method v from EventsAccessor."""

    def test_no_df_ds_mapping_given_to_load(self):
        """Use without having specified df_ds_mapping.

        When no df_ds_mapping is given to load before calling groupby_events,
        ensure that a TypeError is raised.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        with pytest.raises(TypeError):
            (
                ds
                .events.load(events)
                .events.groupby_events('start_frame', 'ball_trajectory')
            )

    def test_no_fill_method(self) -> None:
        """Use with no fill method.

        When no fill_method is given, ensure that the resulting DataArray shows
        intact values from the events DataFrame as expected.

        In this scenario, the mask returned by expand_to_match_ds only contains
        one value per event and everything else is nan. We're applying sum() to
        the Group but that effectively yields the y position at the start_frame
        in question because of the nans.

        Needless to say, this isn't a very wise thing to do since it's easier to
        just get these values from the Dataset by doing

        ds
        .sel(cartesian_coords='y')
        .ball_trajectory
        .sel(frame = list(events['start_frame']))

        But the point is to show that this is still possible.

        ** Should we delete this test AND dump support for this altogether? **

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        result = xr.DataArray(
            data=[0.00033546262790251185, 0.36347375233551676],
            coords={'event_index': [0, 1], 'cartesian_coords': 'y'},
            dims=['event_index'],
            name='ball_trajectory'
        )

        assert_identical(
            ds
            .events.load(events, df_ds_mapping)
            .sel(cartesian_coords='y')
            .events.groupby_events('start_frame', 'ball_trajectory')
            .sum(),
            result
        )

    def test_default_index_mapping_given_ffill(self) -> None:
        """Use filling method ffill.

        When the events DataFrame has no custom index, the mapping is given and
        the filling method is ffill, ensure that the resulting DataArray shows
        groups as expected.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        result = xr.DataArray(
            data=[0.20811694395544034, 6.967413493106037],
            coords={'event_index': [0, 1], 'cartesian_coords': 'x'},
            dims=['event_index'],
            name='ball_trajectory'
        )

        assert_identical(
            ds
            .events.load(events, df_ds_mapping)
            .sel(cartesian_coords='x')
            .events.groupby_events('start_frame', 'ball_trajectory', 'ffill')
            .mean(),
            result
        )

    def test_default_index_mapping_given_nearest(self) -> None:
        """Use filling method nearest.

        When the events DataFrame has no custom index, the mapping is given and
        the filling method is nearest, ensure that the resulting DataArray shows
        groups as expected.

        This filling method can be very useful in situations where there are
        evenly-spaced gaps between the events. In fact, even if the gaps aren't
        evenly-spaced and depending on the data, this filling method *might* be
        useful too.

        In this example, we're grouping by start_frame. Given that they are 1
        and 200, this method will fill 1 up until a point where 200 would also
        fill backwards and both would be evenly distributed. This is convenient
        since the first event finishes at frame 100, so it matches and the
        behavior is correct.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 200],
            'end_frame': [100, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        result = xr.DataArray(
            data=[0.024333249286877082, 3.755349658637451],
            coords={'event_index': [0, 1], 'cartesian_coords': 'x'},
            dims=['event_index'],
            name='ball_trajectory'
        )

        assert_identical(
            ds
            .events.load(events, df_ds_mapping)
            .sel(cartesian_coords='x')
            .events.groupby_events('start_frame', 'ball_trajectory', 'nearest')
            .mean(),
            result
        )

    def test_custom_index_mapping_given_bfill(self) -> None:
        """Use a custom index name and filling method bfill.

        When the events DataFrame has a custom index, the mapping is given and
        the filling method is bfill, ensure that the resulting DataArray shows
        groups as expected.

        Notice that in this example we're grouping by end_frame instead of
        start_frame. It wouldn't make sense otherwise!

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 125],
            'end_frame': [124, 250]
        })

        events.index.name = 'custom_index_name'

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 7, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        result = xr.DataArray(
            data=[0.047471378472240665, 4.443248593601172],
            coords={'custom_index_name': [0, 1], 'cartesian_coords': 'x'},
            dims=['custom_index_name'],
            name='ball_trajectory'
        )

        assert_identical(
            ds
            .events.load(events, df_ds_mapping)
            .sel(cartesian_coords='x')
            .events.groupby_events('end_frame', 'ball_trajectory', 'bfill')
            .mean(),
            result
        )

    def test_dimension_matching_col_invalid(self) -> None:
        """Use an invalid dimension_matching_col.

        When dimension_matching_col isn't a valid events DataFrame column,
        ensure that a KeyError is raised.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        with pytest.raises(KeyError):
            (
                ds
                .events.load(events, df_ds_mapping)
                .events.groupby_events('final_frame', 'ball_trajectory')
                .mean()
            )

    def test_array_to_group_invalid(self) -> None:
        """Use an invalid array_to_group.

        When array_to_group isn't a valid Dataset DataVariable or Coordinate,
        ensure that a KeyError is raised.

        """
        events = pd.DataFrame({
            'event_type_id': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        })

        ds = xr.Dataset(
            data_vars={
                'ball_trajectory': (
                    ['frame', 'cartesian_coords'],
                    np.exp(np.linspace((-6, -8), (3, 2), 250))
                )
            },
            coords={'frame': np.arange(1, 251), 'cartesian_coords': ['x', 'y']},
            attrs={'match_id': 12, 'resolution_fps': 25}
        )

        df_ds_mapping = {'start_frame': 'frame', 'end_frame': 'frame'}

        with pytest.raises(KeyError):
            (
                ds
                .events.load(events, df_ds_mapping)
                .events.groupby_events('start_frame', 'ball_displacement')
                .mean()
            )
