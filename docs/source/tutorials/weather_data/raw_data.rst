Raw data
++++++++

The :obj:`Dataset` consists of temperature data from Barcelona (Spain). The data
goes from March 1st (1) to March 7th (7) in 2020.

The events :obj:`DataFrame` extends the :obj:`Dataset` to add meaning to it. It
describes some notable weather conditions during these dates.

This is how we declare it:

.. jupyter-execute:: raw_data.py

We can visualize the :obj:`Dataset` we're working with.

.. jupyter-execute::

    ax = ds.to_dataframe().T.boxplot()
    ax.set_xlabel("Day")
    ax.set_ylabel("Temperature (Celsius)")
    ax.set_title("Weather in BCN on March 1st-7th 2020.")

In order to use it, let's do some basic setup.

.. jupyter-execute::

    mapping = {'time': ('initial_timestamp', 'final_timestamp')}

    ds = ds.events.load(events, mapping)

This is a very small dataset but still large enough to let us illustrate some
interesting applications of :mod:`xarray-events`.
