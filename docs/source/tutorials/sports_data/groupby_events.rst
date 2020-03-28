Grouping a data variable by the events in the :obj:`DataFrame`
**************************************************************

In this section we're going to illustrate how to use the method
:meth:`groupby_events`.

Let's start by recalling that our :obj:`Dataset` contains the data variable
:attr:`ball_trajectory` that has shows for each frame the cartesian coordinates
of the ball. Our goal in this tutorial is to find out where the majority of
these points lie for each group.

We can start by generating the groups. These groups will tell us which positions
in :attr:`ball_trajectory` correspond to the frames determined by each event.
Then we'll compute the median of them. We can do that like this: ::

    ds
    .events.groupby_events('ball_trajectory')
    .median()

The resulting :obj:`DataArray` looks like this: ::

    <xarray.DataArray 'ball_trajectory' (event_index: 10, cartesian_coords: 2)>
    array([[5.39252098e-03, 7.95626970e-04],
           [1.62105883e-02, 2.70288906e-03],
           [4.21467117e-02, 7.81448485e-03],
           [1.05625415e-01, 2.16889707e-02],
           [1.95479999e-01, 4.29810185e-02],
           [8.34698826e-01, 2.15651098e-01],
           [3.25129820e+00, 9.76995999e-01],
           [6.90622435e+00, 2.25647449e+00],
           [1.36302613e+01, 4.80287169e+00],
           [1.79888284e+01, 6.53714824e+00]])
    Coordinates:
      * cartesian_coords  (cartesian_coords) <U1 'x' 'y'
      * event_index       (event_index) int64 0 1 2 3 4 5 6 7 8 9
