Constraints that specify single values
**************************************

Say we want to select all passes. We can do it like this:

.. jupyter-execute:: ../../raw_data.py
    :hide-code:

.. jupyter-execute::

    (
        ds
        .events.load(events, {'frame': ('start_frame', 'end_frame')})
        .events.sel({'event_type': 'pass'})
        .events.df
    )

See? We are now using the accessor twice, once every time we need to access any
of its methods. First we access the method :meth:`sel` and then the property
:meth:`df`. This is because the result of :meth:`sel` is actually a (stateful)
:obj:`Dataset`, as mentioned before, so we use the accessor again on it in a
chain-like fashion. Very convenient!
