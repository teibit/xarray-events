Constraints that specify single values
**************************************

Say we want to select all passes. We can do it like this: ::

    ds.events.sel({'event_type': 'pass'})

This returns a :obj:`Dataset` object. To actually see the filtered result, we
can do this: ::

    ds
    .events.sel({'event_type': 'pass'})
    .events.df

And the resulting :obj:`DataFrame` looks like this:

=======     ==========  =========== =========   =========
(index)     event_type  start_frame end_frame   player_id
=======     ==========  =========== =========   =========
0           pass        1           424         79
2           pass        600         944         19
3           pass        945         1099        2
4           pass        1100        1279        3
7           pass        2020        2299        79
8           pass        2300        2389        2
=======     ==========  =========== =========   =========

See? We are now using the accessor twice, once every time we need to access any
of its methods. First we access the method
:meth:`~.xarray_events.EventsAccessor.sel` and then the property
:meth:`~.xarray_events.EventsAccessor.df`. This is because the result of
:meth:`~.xarray_events.EventsAccessor.sel` is actually a (stateful)
:obj:`Dataset`, as mentioned before, so we use the accessor again on it in a
chain-like fashion. Very convenient!
