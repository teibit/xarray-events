import numpy as np
import pandas as pd
import xarray as xr
import xarray_events

ds = xr.Dataset(
    data_vars={
        'ball_trajectory': (
            ['frame', 'cartesian_coords'],
            np.exp(np.linspace((-6, -8), (3, 2), 2450))
        )
    },
    coords={
        'frame': np.arange(1, 2451),
        'cartesian_coords': ['x', 'y'],
        'player_id': [2, 3, 7, 19, 20, 21, 22, 28, 34, 79]
    },
    attrs={'match_id': 12, 'resolution_fps': 25}
)

events = pd.DataFrame(
    {
        'event_type':
            ['pass', 'goal', 'pass', 'pass', 'pass',
             'penalty', 'goal', 'pass', 'pass', 'penalty'],
        'start_frame': [1, 425, 600, 945, 1100, 1280, 1890, 2020, 2300, 2390],
        'end_frame': [424, 599, 944, 1099, 1279, 1889, 2019, 2299, 2389, 2450],
        'player_id': [79, 79, 19, 2, 3, 2, 3, 79, 2, 79]
    }
)
