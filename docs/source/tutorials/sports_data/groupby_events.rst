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
Then we'll compute the median of them. We can do that like this:

.. jupyter-execute:: raw_data.py
    :hide-code:

.. jupyter-execute::

    (
        ds
        .events.load(events, {'frame': ('start_frame', 'end_frame')})
        .events.groupby_events('ball_trajectory')
        .median()
    )
