"""Unit tests for the integrity of the events :mod:`DataFrame`.

Usage: Assuming the current directory is the top one,

    $ pytest -q tests -ra

    will run all tests and provide a short summary that ignores passed ones and
    any captured console output.

    To run this specific test file, simply do

    $ pytest -q tests/events_integrity_test.py -ra

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


def test_there_are_gaps_1() -> None:
    """Check that an events DataFrame contains gaps."""
    events = pd.DataFrame(
        {
            'event_type': ['pass'],
            'start_frame': [50],
            'end_frame': [299]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 300))
            )
        },
        coords={'frame': np.arange(1, 301), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    assert ds.events.load(events, ds_df_mapping).events.df_contains_gaps()


def test_there_are_gaps_but_no_duration_mapping() -> None:
    """Check that an error is raised when there is no duration mapping."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [50, 175],
            'end_frame': [300, 450]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 500))
            )
        },
        coords={'frame': np.arange(0, 500), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': 'start_frame'}

    with pytest.raises(TypeError):
        (
            ds
            .events.load(events, ds_df_mapping)
            .events.df_contains_gaps()
        )


def test_there_are_gaps_2() -> None:
    """Check that an events DataFrame contains gaps."""
    events = pd.DataFrame(
        {
            'event_type': ['pass'],
            'start_frame': [1],
            'end_frame': [249]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 300))
            )
        },
        coords={'frame': np.arange(1, 301), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    assert ds.events.load(events, ds_df_mapping).events.df_contains_gaps()


def test_there_are_gaps_3() -> None:
    """Check that an events DataFrame contains gaps."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 229],
            'end_frame': [149, 300]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 300))
            )
        },
        coords={'frame': np.arange(1, 301), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    assert ds.events.load(events, ds_df_mapping).events.df_contains_gaps()


def test_get_duration_no_mapping() -> None:
    """Try getting duration when no ds_df_mapping has been given."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 229],
            'end_frame': [149, 300]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 300))
            )
        },
        coords={'frame': np.arange(1, 301), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    with pytest.raises(TypeError):
        (
            ds
            .events.load(events)
            .events.duration_mapping
        )


def test_get_duration_multiple_mappings() -> None:
    """Try getting duration when multiple mappings have been given."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 229],
            'end_frame': [149, 300],
            'initial_position': [
                [0.00247875, 0.00033546],
                [2.36996753, 0.68757667]
            ],
            'final_position': [
                [0.21327977, 0.04735101],
                [20.08553692, 7.3890561]
            ]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 300))
            )
        },
        coords={'frame': np.arange(1, 301), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {
        'frame': ('start_frame', 'end_frame'),
        'cartesian_coords': ('initial_position', 'final_position')
    }

    with pytest.raises(ValueError):
        (
            ds
            .events.load(events, ds_df_mapping)
            .events.duration_mapping
        )


def test_there_are_no_gaps() -> None:
    """Check that an events DataFrame doesn't contain gaps."""
    events = pd.DataFrame(
        {
            'event_type': ['pass'],
            'start_frame': [1],
            'end_frame': [300]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 300))
            )
        },
        coords={'frame': np.arange(1, 301), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    assert not ds.events.load(events, ds_df_mapping).events.df_contains_gaps()


def test_there_are_no_gaps_2() -> None:
    """Check that an events DataFrame doesn't contain gaps."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 120],
            'end_frame': [119, 300]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 300))
            )
        },
        coords={'frame': np.arange(1, 301), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    assert not ds.events.load(events, ds_df_mapping).events.df_contains_gaps()


def test_gaps_are_filled() -> None:
    """Check the correct behavior of fill_gaps."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [50, 300],
            'end_frame': [175, 450]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 500))
            )
        },
        coords={'frame': np.arange(0, 500), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    events_no_gaps = pd.DataFrame({
        'event_type': ['pass', 'goal', 'default', 'default', 'default'],
        'start_frame': [50, 300, 0, 176, 451],
        'end_frame': [175, 450, 49, 299, 499]
    })

    assert_frame_equal(
        ds
        .events.load(events, ds_df_mapping)
        .events.fill_gaps()
        .events.df,
        events_no_gaps
    )


def test_that_gaps_are_filled_despite_no_duration_mapping() -> None:
    """Check that an error is raised when there is no duration mapping."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [50, 175],
            'end_frame': [300, 450]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 500))
            )
        },
        coords={'frame': np.arange(0, 500), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': 'start_frame'}

    with pytest.raises(TypeError):
        (
            ds
            .events.load(events, ds_df_mapping)
            .events.fill_gaps()
        )


def test_nonconsecutive_integers_gaps_are_filled() -> None:
    """Check the correct behavior of fill_gaps with nonconsecutive values."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'pass'],
            'start_frame': [0, 8],
            'end_frame': [2, 10]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 6))
            )
        },
        coords={
            'frame': np.arange(0, 12, 2),
            'cartesian_coords': ['x', 'y']
        },
        attrs={'match_id': 9, 'resolution_fps': 1}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    events_no_gaps = pd.DataFrame(
        {
            'event_type': ['pass', 'pass', 'default'],
            'start_frame': [0, 8, 4],
            'end_frame': [2, 10, 6]
        }
    )

    assert_frame_equal(
        ds
        .events.load(events, ds_df_mapping)
        .events.fill_gaps()
        .events.df,
        events_no_gaps
    )


def test_nonconsistent_integers_gaps_are_filled() -> None:
    """Check the correct behavior of fill_gaps with nonconsecutive values."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'pass'],
            'start_frame': [4, 36],
            'end_frame': [9, 49]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 10))
            )
        },
        coords={
            'frame': np.square(np.arange(0, 10)),
            'cartesian_coords': ['x', 'y']
        },
        attrs={'match_id': 9, 'resolution_fps': 1}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    events_no_gaps = pd.DataFrame(
        {
            'event_type': ['pass', 'pass', 'default', 'default', 'default'],
            'start_frame': [4, 36, 0, 16, 64],
            'end_frame': [9, 49, 1, 25, 81]
        }
    )

    assert_frame_equal(
        ds
        .events.load(events, ds_df_mapping)
        .events.fill_gaps()
        .events.df,
        events_no_gaps
    )


def test_float_values_gaps_are_filled() -> None:
    """Check the correct behavior of fill_gaps with floats."""
    events = pd.DataFrame(
        {
            'event_kind': ['pass', 'pass'],
            'start_frame': [4.9, 36.1],
            'end_frame': [9.0, 49.49]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 10))
            )
        },
        coords={
            'frame': [0.0, 1.4, 4.9, 9.0, 16.2, 25.43, 36.1, 49.49, 64.0, 81.5],
            'cartesian_coords': ['x', 'y']
        },
        attrs={'match_id': 9, 'resolution_fps': 1}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    events_no_gaps = pd.DataFrame(
        {
            'event_kind': [
                'pass', 'pass', 'outOfScope', 'outOfScope', 'outOfScope'
            ],
            'start_frame': [4.9, 36.1, 0.0, 16.2, 64.0],
            'end_frame': [9.0, 49.49, 1.4, 25.43, 81.5],
            'category': [np.nan, np.nan, 5, 5, 5]
        }
    )

    assert_frame_equal(
        ds
        .events.load(events, ds_df_mapping)
        .events.fill_gaps('event_kind', 'outOfScope', {'category': 5})
        .events.df,
        events_no_gaps
    )


def test_there_are_overlapping_events_but_no_duration_mapping() -> None:
    """Check that an error is raised when there is no duration mapping."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [50, 175],
            'end_frame': [300, 450]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 500))
            )
        },
        coords={'frame': np.arange(0, 500), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': 'start_frame'}

    with pytest.raises(TypeError):
        (
            ds
            .events.load(events, ds_df_mapping)
            .events.df_contains_overlapping_events()
        )


def test_there_are_overlapping_events() -> None:
    """Check that an events DataFrame contains overlapping events."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [50, 175],
            'end_frame': [300, 450]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 500))
            )
        },
        coords={'frame': np.arange(0, 500), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    assert (
        ds
        .events.load(events, ds_df_mapping)
        .events.df_contains_overlapping_events()
    )


def test_there_are_overlapping_events_2() -> None:
    """Check that an events DataFrame contains overlapping events."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [50, 25],
            'end_frame': [450, 300]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 500))
            )
        },
        coords={'frame': np.arange(0, 500), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    assert (
        ds
        .events.load(events, ds_df_mapping)
        .events.df_contains_overlapping_events()
    )


def test_there_are_overlapping_events_3() -> None:
    """Check that an events DataFrame contains overlapping events."""
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [50, 50],
            'end_frame': [450, 450]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 500))
            )
        },
        coords={'frame': np.arange(0, 500), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    assert (
        ds
        .events.load(events, ds_df_mapping)
        .events.df_contains_overlapping_events()
    )
