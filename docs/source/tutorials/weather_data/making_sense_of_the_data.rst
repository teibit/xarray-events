Making sense of the data
++++++++++++++++++++++++

Let's now see how we could use this API to answer a basic question aimed to get
more insight of the data.

-   What's the per-event daily mean temperature?

.. jupyter-execute:: raw_data.py
    :hide-code:

.. jupyter-execute::
    :hide-code:

    mapping = {'time': ('initial_timestamp', 'final_timestamp')}

    ds = ds.events.load(events, mapping)

.. jupyter-execute::

    per_event_min = ds.events.groupby_events('tmin').min()
    per_event_max = ds.events.groupby_events('tmax').max()
    per_event_mean = ((per_event_min + per_event_max) / 2)

    ax = (
        per_event_mean
        .rename('per-event mean temp')
        .to_dataframe()
        .reset_index()
        .set_index(ds.events.df.event_type)
        ['per-event mean temp']
        .plot
        .bar(x=0, rot=0)
    )

    ax.set_xlabel("Event")
    ax.set_ylabel("Temperature (Celsius)")
    ax.set_title("Per-event daily mean temperature.")
