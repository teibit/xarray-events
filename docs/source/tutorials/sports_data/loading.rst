Loading
*******

We can load the events :obj:`DataFrame` into our :obj:`Dataset` like this:

.. jupyter-execute:: raw_data.py
    :hide-code:

.. jupyter-execute::

    ds = ds.events.load(events)

At this point, :data:`ds` contains the (private) attribute :attr:`_events`
storing :data:`events`.

.. jupyter-execute::

    ds
