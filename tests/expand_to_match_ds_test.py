"""Unit tests for meth:`expand_to_match_ds`.

Usage: Assuming the current directory is the top one,

    $ pytest -q tests -ra

    will run all tests and provide a short summary that ignores passed ones and
    any captured console output.

    To run this specific test file, simply do

    $ pytest -q tests/expand_to_match_ds_test.py -ra

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

import warnings


def test_expand_no_ds_df_mapping_given_to_load() -> None:
    """Use without having specified ds_df_mapping.

    When no ds_df_mapping is given to load before calling expand_to_match_ds,
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
            .events.expand_to_match_ds('end_frame', 'bfill')
        )


def test_no_fill_method() -> None:
    """Use no fill method.

    When no fill_method is given, ensure that the resulting DataArray shows
    intact values from the events DataFrame and lots of nans as expected.

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250],
            'peak_frame': [133, 189]
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

    ds_df_mapping = {'frame': [('start_frame', 'end_frame'), 'peak_frame']}

    result = xr.DataArray(
        data=[0] + [np.nan] * 173 + [1] + [np.nan] * 75,
        coords={'frame': np.arange(1, 251)},
        dims=['frame'],
        name='event_index'
    )

    assert_identical(
        ds
        .events.load(events, ds_df_mapping)
        .events.expand_to_match_ds('start_frame'),
        result
    )


def test_custom_index_mapping_given_ffill() -> None:
    """Use a custom index name and the filling method ffill.

    When the filling method is 'ffill', ensure that the resulting DataArray
    is filled appropriately.

    In this scenario, changing this filling method changes the output
    dramatically without introducing nans.

    """
    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal'],
            'start_frame': [1, 175],
            'end_frame': [174, 250]
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
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    result = xr.DataArray(
        data=[0] * 174 + [1] * 76,
        coords={'frame': np.arange(1, 251)},
        dims=['frame'],
        name='custom_index_name'
    )

    assert_identical(
        ds
        .events.load(events, ds_df_mapping)
        .events.expand_to_match_ds('start_frame', 'ffill', 'custom_index_name'),
        result
    )


def test_reloading_ds_df_mapping() -> None:
    """Try to load ds_df_mapping when it already exists."""
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
        attrs={
            'match_id': 12,
            'resolution_fps': 25,
            # Assume the user loads _ds_df_mapping with some value.
            '_ds_df_mapping': {'frame': 'end_frame'}
        }
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    with pytest.warns(UserWarning):
        (
            ds
            .events.load(events, ds_df_mapping)
            .events.expand_to_match_ds('end_frame', 'bfill')
        )


def test_default_index_mapping_given_ffill_gaps() -> None:
    """Use ffill with events with gaps.

    When the filling method is 'ffill', ensure that the gaps in the events
    DataFrame are filled and the resulting DataArray is filled
    appropriately afterwards.

    The gaps are defined as the data not covered by the duration of all of
    the events combined. They're filled by creating new events.

    """
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

    # 2 2 ...  2  0  0 ...   0   3   3 ...   3   1   1 ...   1   4 ...   4
    # 0 1 ... 49 50 51 ... 175 176 177 ... 299 300 301 ... 450 451 ... 499

    result = xr.DataArray(
        data=(
            [2] * 50 +  # filler
            [0] * 126 +
            [3] * 124 +  # filler
            [1] * 151 +
            [4] * 49  # filler
        ),
        coords={'frame': np.arange(0, 500)},
        dims=['frame'],
        name='event_index'
    )

    assert_identical(
        ds
        .events.load(events, ds_df_mapping)
        .events.fill_gaps()
        .events.expand_to_match_ds('start_frame', 'ffill'),
        result
    )


def test_default_index_mapping_given_bfill_gaps() -> None:
    """Use bfill with events with gaps.

    When the filling method is 'bfill', ensure that the gaps in the events
    DataFrame are filled and the resulting DataArray is filled
    appropriately afterwards.

    The gaps are defined as the data not covered by the duration of all of
    the events combined. They're filled by creating new events.

    """
    events = pd.DataFrame({
        'event_type': ['pass', 'goal'],
        'start_frame': [50, 300],
        'end_frame': [175, 450]
    })

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

    result = xr.DataArray(
        data=(
            [2] * 50 +  # filler
            [0] * 126 +
            [3] * 124 +  # filler
            [1] * 151 +
            [4] * 49  # filler
        ),
        coords={'frame': np.arange(0, 500)},
        dims=['frame'],
        name='event_index'
    )

    assert_identical(
        ds
        .events.load(events, ds_df_mapping)
        .events.fill_gaps()
        .events.expand_to_match_ds('end_frame', 'bfill'),
        result
    )


def test_default_index_mapping_given_nearest() -> None:
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
        attrs={'match_id': 12, 'resolution_fps': 25}
    )

    ds_df_mapping = {'frame': ('start_frame', 'end_frame')}

    result = xr.DataArray(
        data=[0] * 100 + [1] * 150,
        coords={'frame': np.arange(1, 251)},
        dims=['frame'],
        name='event_index'
    )

    assert_identical(
        ds
        .events.load(events, ds_df_mapping)
        .events.expand_to_match_ds('start_frame', 'nearest'),
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
            .events.expand_to_match_ds('starting_frame')
        )


def test_fill_value_col_invalid() -> None:
    """Use an invalid fill_value_col.

    When fill_value_col isn't a valid events DataFrame column, ensure that a
    KeyError is raised.

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
            .events.expand_to_match_ds('start_frame', 'ffill', 'event_id')
        )
