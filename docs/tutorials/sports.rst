Sports data
***********

In this tutorial we'll be working with sports data.

Raw data
++++++++

:py:obj:`Dataset`
-----------------

We're going to work with a :py:obj:`Dataset` that describes a football match
consisting of the following:

-   The following two coordinates:

    -   The *frame* at which the ball is at. There are 250 possible frames in
        this recording.
    -   The *cartesian coordinates* (x,y) of the ball's position.

-   A :py:obj:`DataVariable` that describes the *trajectory* of the ball. It is
    described by the two coordinates of the :py:obj:`Dataset`.

-   The following two attributes:

    -   The match ID, which is 12.
    -   The resolution (25 Hz) of the recording in frames per second.

We can create it manually like this: ::

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

The object looks like this: ::

    <xarray.Dataset>
    Dimensions:           (cartesian_coords: 2, frame: 2450)
    Coordinates:
      * frame             (frame) int64 1 2 3 4 5 6 ... 2446 2447 2448 2449 2450
      * cartesian_coords  (cartesian_coords) <U1 'x' 'y'
    Data variables:
        ball_trajectory   (frame, cartesian_coords) float64 0.002479 ... 7.389
    Attributes:
        match_id:        12
        resolution_fps:  25

Events
------

We're going to create events directly in a :py:obj:`DataFrame` consisting of the
following attributes:

-   The event *type*, which can be: penalty, pass or goal.

-   The frame where the event starts.

-   The frame where the event ends.

-   The ID of the responsible player.

We can create it manually like this: ::

    events = pd.DataFrame({
        'event_type_id': ['penalty', 'pass', 'goal'],
        'start_frame': [1, 425, 600, 945, 1100, 1280, 1890, 2020, 2300, 2390],
        'end_frame': [424, 599, 944, 1099, 1279, 1889, 2019, 2299, 2389, 2450],
        'player_id': []
    })

The object is just a table that looks like this:

=======     ==========  =========== =========   =========
(index)     event_type  start_frame end_frame   player_id
=======     ==========  =========== =========   =========
0           pass        1           424         79
1           goal        425         599         79
2           pass        600         944         19
3           pass        945         1099        2
4           pass        1100        1279        3
5           penalty     1280        1889        2
6           goal        1890        2019        3
7           pass        2020        2299        79
8           pass        2300        2389        2
9           penalty     2390        2450        79
=======     ==========  =========== =========   =========

Loading
-------

We can load the events :py:obj:`DataFrame` into our :py:obj:`Dataset` like
this: ::

    ds = ds.events.load(events)

At this point, :py:attr:`_ds` contains the private attribute :py:attr:`_events`
storing :py:const:`events`.

Selecting
---------

We now move on to the most popular action in :py:mod:`xarray`: selection. Here
is where we start grasping the benefits of :py:mod:`xarray-events`. The method
provided by :py:mod:`xarray` is very powerful and useful when we need to perform
selections on a :py:obj:`Dataset` only. However, the exended :py:meth:`sel` in
:py:mod:`xarray-events` allows you to make selections that also take into
account the existance of events data.

Say we want to select all passes. We can do it like this: ::

    ds.events.sel({'event_type': 'pass'})

This returns a :py:obj:`Dataset` object. To actually see the filtered result,
we can do this: ::

    ds.events.sel({'event_type': 'pass'}).events.df

See? We are now using the accessor twice, once every time we need to access any
of its methods. First we access the method :py:meth:`sel` and then the property
:py:obj:`df`. This is because the result of :py:meth:`sel` is actually a
(stateful) :py:obj:`Dataset`, as mentioned before, so we use the accessor again
on it in a chain-like fashion. Very convenient!
