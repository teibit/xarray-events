Constraints that match everything
+++++++++++++++++++++++++++++++++

Let's now see how we put together all of the functionality of our accessor to
make useful (though complex) queries.

Given that now :meth:`~.xarray_events.EventsAccessor.sel` considers two
different search spaces (i.e. the events :obj:`DataFrame` and the
:obj:`Dataset`), we can make the search be so complex that it searches in both
spaces. This is a powerful feature of our accessor.

Say we may wish to perform a selection with the following specification:

-   An event of type *pass*.
-   The frames are within 1728 and 2378.

Moreover, we want the result to be consistent across the :obj:`Dataset` and the
events :obj:`DataFrame`. In that case, we can achieve this like this: ::

    ds
    .events.sel({
        'frame': range(1729, 2378),
        'start_frame': lambda frame: frame > 1728,
        'end_frame': lambda frame: frame < 2378,
        'event_type': 'pass'
    })

Internally, :meth:`~.xarray_events.EventsAccessor.sel` filters the events
:obj:`DataFrame` and also the :obj:`Dataset`, each with its corresponding
attributes.

The resulting :obj:`Dataset` looks like this: ::

    <xarray.Dataset>
    Dimensions:           (cartesian_coords: 2, frame: 650, player_id: 10)
    Coordinates:
      * frame             (frame) int64 1728 1729 1730 1731 ... 2374 2375 2376 2377
      * cartesian_coords  (cartesian_coords) <U1 'x' 'y'
      * player_id         (player_id) int64 2 3 7 19 20 21 22 28 34 79
    Data variables:
        ball_trajectory   (frame, cartesian_coords) float64 1.414 0.3875 ... 5.484
    Attributes:
        match_id:        12
        resolution_fps:  25
        _events:           event_type  start_frame  end_frame  player_id\n7      ...

And the resulting :obj:`DataFrame` looks like this:

=======     ==========  =========== =========   =========
(index)     event_type  start_frame end_frame   player_id
=======     ==========  =========== =========   =========
7           pass        2020        2299        79
=======     ==========  =========== =========   =========

We want to emphasize how we give the user the power to do things exactly as they
want them since the constraints have to be properly specified for both the
:obj:`Dataset` and also the :obj:`DataFrame`.
:meth:`~.xarray_events.EventsAccessor.sel` does not assume that they may want to
select both or anything like that. It all must be specified. This provides great
flexibility.
