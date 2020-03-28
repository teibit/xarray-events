Expanding an events column to match the :obj:`Dataset`'s shape
**************************************************************

In this section we're going to demonstrate how to use
:meth:`~.xarray_events.EventsAccessor.expand_to_match_ds`. Some observations
first:

-   The events :obj:`DataFrame` doesn't have a custom index name, so we're going
    to let :attr:`fill_value_col` be "event_index".

-   We're going to fill the output :obj:`DataArray` with the index of each event
    in a forward-fill way. It's important that this column be unique, which is
    the case this way.

-   We're going to use `start_frame` as the :attr:`dimension_matching_col` by
    previously specifying that it maps to :attr:`frame` in the :obj:`Dataset`.
    This mapping is consistent since the values of `start_frame` form a subset
    of the values of :obj:`Dataset`.

By calling :meth:`~.xarray_events.EventsAccessor.expand_to_match_ds` this way
we'll be constructing a :obj:`DataArray` with the following properties:

-   The coordinate is :attr:`frame`.

-   At each position, there's the (unique) index of each event repeated forward
    until a new index needs to be placed. Therefore, **each value represents the
    event that is currently taking place at the frame determined by the
    coordinate**.

To do this, we first need to make sure to call
:meth:`~.xarray_events.EventsAccessor.load` specifying the mapping and then call
:meth:`~.xarray_events.EventsAccessor.expand_to_match_ds` with the values
already discussed: ::

    ds
    .events.load(events, {'start_frame': 'frame'})
    .events.expand_to_match_ds('start_frame', 'event_index', 'ffill')

This will produce the following :obj:`DataArray`: ::

    <xarray.DataArray 'event_index' (frame: 2450)>
    array([0, 0, 0, ..., 9, 9, 9])
    Coordinates:
    * frame    (frame) int64 1 2 3 4 5 6 7 ... 2444 2445 2446 2447 2448 2449 2450
