"""Unit tests for meth:`load`.

Usage: Assuming the current directory is the top one,

    $ pytest -q tests -ra

    will run all tests and provide a short summary that ignores passed ones and
    any captured console output.

    To run this specific test file, simply do

    $ pytest -q tests/load_test.py -ra

    instead.

"""
import numpy as np

import pandas as pd
from pandas.testing import assert_frame_equal

import pytest

import xarray as xr
from xarray.testing import assert_identical
from xarray.testing import assert_equal

import xarray_events


def test_from_DataFrame() -> None:
    """Use a DataFrame.

    When load is called with a DataFrame as an argument, ensure that it adds
    the attribute _events to the Dataset with the provided value.

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

    assert_frame_equal(
        ds
        .events.load(events)
        .events._ds._events,
        events
    )


def test_wrong_df() -> None:
    """Use an invalid DataFrame.

    When the provided ds_df_mapping contains invalid event DataFrame
    columns, ensure that a ValueError is raised.

    """
    events = pd.DataFrame({
        'event_type': ['pass', 'goal'],
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

    ds_df_mapping = {'frame': ('starting_frame', 'finishing_frame')}

    with pytest.raises(ValueError):
        ds.events.load(events, ds_df_mapping)


def test_valid_mapping() -> None:
    """Use a correct mapping.

    When ds_df_mapping is correctly provided, ensure that it is correctly
    stored.

    """
    events = pd.DataFrame({
        'event_type': ['pass', 'goal'],
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

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    result = ds.assign_attrs(_events=events, _ds_df_mapping=ds_df_mapping)

    assert_identical(
        ds.events.load(events, ds_df_mapping),
        result
    )


def test_wrong_ds() -> None:
    """Use an invalid Dataset.

    When the provided ds_df_mapping contains invalid Dataset dimensions or
    coordinates, ensure that a ValueError is raised.

    """
    events = pd.DataFrame({
        'event_type': ['pass', 'goal'],
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

    ds_df_mapping = {'f': ('start_frame', 'end_frame')}

    with pytest.raises(ValueError):
        ds.events.load(events, ds_df_mapping)
