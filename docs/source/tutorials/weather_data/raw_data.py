import numpy as np
import pandas as pd
import xarray as xr
import xarray_events


tmin_values = [13, 10, 8, 10, 10, 8, 7]

tmax_values = [21, 18, 17, 16, 19, 17, 18]

ds = xr.Dataset(
    data_vars={
        'tmin': ('time', tmin_values),
        'tmax': ('time', tmax_values),
    },
    coords={'time': np.arange(1, 8)},
    attrs={'temperature_system': 'celcious', 'location': 'BCN'}
)

events = pd.DataFrame(
    {
        'event_type': ['light-rain-shower', 'patchy-rain-possible'],
        'initial_timestamp': [1, 4],
        'final_timestamp': [3, 5]
    }
)
