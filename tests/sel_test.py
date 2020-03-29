"""Unit tests for meth:`sel`.

Usage: Assuming the current directory is the top one,

    $ pytest -q tests -ra

    will run all tests and provide a short summary that ignores passed ones and
    any captured console output.

    To run this specific test file, simply do

    $ pytest -q tests/sel_test.py -ra

    instead.

"""
import numpy as np

import pandas as pd
from pandas.testing import assert_frame_equal

import pytest

from typing import Any, Hashable, Mapping, Optional

import xarray as xr
from xarray.testing import assert_identical
from xarray.testing import assert_equal

import xarray_events

import warnings


def test_sel_args_match_nothing() -> None:
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

    with pytest.raises(KeyError):
        ds.events.sel(selection)


def test_args_ok_dims_wrong_events() -> None:
    """Use an invalid events DataFrame attribute.

    When the dictionary of constraints refers to correct dimensions or
    coordinates of the Dataset but incorrect events DataFrame attribute,
    ensure that a ValueError is thrown.

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        }
    )

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

    with pytest.raises(KeyError):
        (
            ds
            .events.load(events)
            .events.sel(selection)
        )


def test_no_df() -> None:
    """Try retrieving the events DataFrame when it hasn't been loaded."""
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

    with pytest.raises(TypeError):
        ds.events.df


def test_args_wrong_dims_ok_events() -> None:
    """Use an invalid Dataset dimension or coordinate.

    When the dictionary of constraints refers to incorrect dimensions or
    coordinates of the Dataset but correct events DataFrame attribute,
    ensure that a ValueError is thrown.

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        }
    )

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

    with pytest.raises(KeyError):
        (
            ds
            .events.load(events)
            .events.sel(selection)
        )


def test_args_match_only_dims() -> None:
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

    assert_identical(
        ds.events.sel(selection),
        ds.sel(selection)
    )


def test_args_match_only_events() -> None:
    """Match exclusively an events DataFrame attribute.

    When the dictionary of constraints refers exclusively to event attrs,
    ensure that the selection result filters the events DataFrame with the
    matching attrs and the Dataset stays the same.

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        }
    )

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
    assert_equal(
        ds.events.sel(selection),
        ds
    )


def test_args_match_both_dims_events() -> None:
    """Match Dataset dimension/coordinate and events DataFrame attribute.

    When the dictionary of constraints refers to both dimensions or
    coordinates of the Dataset and attributes of the events DataFrame,
    ensure that the selection result is the same as if we:
        1. make a selection on the dimensions with the matching coords
        2. filter the events DataFrame with the matching attrs

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        }
    )

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
    assert_equal(
        actual_result,
        expected_result
    )

    # Ensure that the Datasets' _events attribute is equal.
    assert_frame_equal(
        actual_result.events.df,
        expected_result._events
    )


def test_single_arg_matches_both_dims_events() -> None:
    """Match Dataset dimension/coordinate and events DataFrame attribute.

    When the dictionary of constraints refers to both a dimension or
    coordinate of the Dataset and an attribute of the events DataFrame,
    ensure that the selection result returns a Dataset in which the
    constraint was correctly enforced in both the Dataset dimension or
    coordinate and also in the DataFrame.

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        }
    )

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
    assert_equal(
        actual_result,
        expected_result
    )

    # Ensure that the Datasets' _events attribute is equal.
    assert_frame_equal(
        actual_result.events.df,
        expected_result._events
    )


def test_args_match_both_dims_args() -> None:
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


def test_args_match_dims_args_events() -> None:
    """Match every possible thing.

    When the dictionary of constraints refers to Dataset dimensions or
    coordinates, method args and attributes of the events DataFrame, ensure
    that the selection
        1. calls xr.Dataset.sel with
            1-1. the matching coords
            1-2. the matching method args
        2. filters the events DataFrame with the matching attrs

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        }
    )

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
    assert_equal(
        actual_result,
        expected_result
    )

    # Ensure that the Datasets' _events attribute is equal.
    assert_frame_equal(
        actual_result.events.df,
        expected_result._events
    )


def test_constraint_is_Collection() -> None:
    """Specify a Collection as a constraint value.

    When the values of the dictionary of constraints refer to a Collection,
    ensure that the events are properly filtered by all of these values.

    For this test, the constraints match only event DataFrame attrs.

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        }
    )

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
    assert_equal(
        ds.events.sel(selection),
        ds
    )


def test_df_constraint_is_Callable() -> None:
    """Specify a Callable as a constraint value.

    When the values of the dictionary of constraints refer to a Callable,
    ensure that the events are properly filtered by this.

    For this test, the constraints match only event DataFrame attrs.

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
        }
    )

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

    selection = {'start_frame': lambda frame: frame == 1}

    # check that the events DataFrames are the same
    assert_frame_equal(
        ds
        .events.load(events)
        .events.sel(selection)
        .events._ds._events,
        events[events['start_frame'] == 1]
    )


def test_ds_constraint_is_Callable() -> None:
    """Specify a Callable as a constraint value for the Dataset."""
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

    selection = {'frame': lambda frame: frame == 1}

    with pytest.raises(KeyError):
        ds.events.sel(selection)
