"""Unit tests for meth:`groupby_events`.

Usage: Assuming the current directory is the top one,

    $ pytest -q tests -ra

    will run all tests and provide a short summary that ignores passed ones and
    any captured console output.

    To run this specific test file, simply do

    $ pytest -q tests/groupby_events_test.py -ra

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


def test_groupby_no_ds_df_mapping_given_to_load() -> None:
    """Use without having specified ds_df_mapping.

    When no ds_df_mapping is given to load before calling groupby_events,
    ensure that a TypeError is raised.

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

    with pytest.raises(TypeError):
        (
            ds
            .events.load(events)
            .events.groupby_events('ball_trajectory', 'start_frame', 'ffill')
        )


def test_default_index_mapping_given_ffill() -> None:
    """Use filling method ffill.

    When the events DataFrame has no custom index, the mapping is given and
    the filling method is ffill, ensure that the resulting DataArray shows
    groups as expected.

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

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    result = xr.DataArray(
        data=[0.20811694395544034, 6.967413493106037],
        coords={'event_index': [0, 1], 'cartesian_coords': 'x'},
        dims=['event_index'],
        name='ball_trajectory'
    )

    assert_identical(
        ds
        .events.load(events, ds_df_mapping)
        .sel(cartesian_coords='x')
        .events.groupby_events('ball_trajectory', 'start_frame', 'ffill')
        .mean(),
        result
    )


def test_groupby_events_default_index_overlapping_events() -> None:
    """Use filling method ffill.

    When the events DataFrame has no custom index, the mapping is given and
    the filling method is ffill, ensure that the resulting DataArray shows
    groups as expected.

    Note: this result could be obtained by doing:

    ds
    .ball_trajectory
    .sel(frame=slice(75, 250))
    .mean('frame')

    for example.

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 75],
            'end_frame': [200, 250]
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

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    result = xr.DataArray(
        data=[
            [0.46392810818556895, 0.12595967267321653],
            [3.209238938587539, 1.0656072898406097]
        ],
        coords={'event_index': [0, 1], 'cartesian_coords': ['x', 'y']},
        dims=['event_index', 'cartesian_coords'],
        name='ball_trajectory'
    )

    assert_identical(
        ds
        .events.load(events, ds_df_mapping)
        .events.groupby_events('ball_trajectory')
        .mean(),
        result
    )


def test_default_index_mapping_given_nearest() -> None:
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
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 200],
            'end_frame': [100, 250]
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

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    result = xr.DataArray(
        data=[0.024333249286877082, 9.338163817766421],
        coords={'event_index': [0, 1], 'cartesian_coords': 'x'},
        dims=['event_index'],
        name='ball_trajectory'
    )

    assert_identical(
        ds
        .events.load(events, ds_df_mapping)
        .sel(cartesian_coords='x')
        .events.groupby_events('ball_trajectory', 'start_frame', 'nearest')
        .mean(),
        result
    )


def test_custom_index_mapping_given_bfill() -> None:
    """Use a custom index name and filling method bfill.

    When the events DataFrame has a custom index, the mapping is given and
    the filling method is bfill, ensure that the resulting DataArray shows
    groups as expected.

    Notice that in this example we're grouping by end_frame instead of
    start_frame. It wouldn't make sense otherwise!

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 125],
            'end_frame': [124, 250]
        }
    )

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

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    result = xr.DataArray(
        data=[0.047471378472240665, 4.443248593601172],
        coords={'custom_index_name': [0, 1], 'cartesian_coords': 'x'},
        dims=['custom_index_name'],
        name='ball_trajectory'
    )

    assert_identical(
        ds
        .events.load(events, ds_df_mapping)
        .sel(cartesian_coords='x')
        .events.groupby_events('ball_trajectory', 'end_frame', 'bfill')
        .mean(),
        result
    )


def test_dimension_matching_col_invalid() -> None:
    """Use an invalid dimension_matching_col.

    When dimension_matching_col isn't a valid events DataFrame column,
    ensure that a KeyError is raised.

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

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    with pytest.raises(KeyError):
        (
            ds
            .events.load(events, ds_df_mapping)
            .events.groupby_events('ball_trajectory', 'final_frame', 'bfill')
            .mean()
        )


def test_array_to_group_invalid() -> None:
    """Use an invalid array_to_group.

    When array_to_group isn't a valid Dataset DataVariable or Coordinate,
    ensure that a KeyError is raised.

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

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    with pytest.raises(KeyError):
        (
            ds
            .events.load(events, ds_df_mapping)
            .events.groupby_events('ball_displacement', 'start_frame', 'ffill')
            .mean()
        )
