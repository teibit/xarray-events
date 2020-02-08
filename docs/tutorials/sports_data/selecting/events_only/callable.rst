Constraints that specify *lambda functions*
*******************************************

Selecting ranges in the events :obj:`DataFrame` is possible. We provide support
for lambda functions in order to empower the user to specify arbitrary
conditions. In the example below we're going to use a simple condition but,
evidently, it can be as complex as needed.

Say we want to select all events that occurred between frames 327 and 1327. We
can do it like this: ::

    ds
    .events.sel({
        'start_frame': lambda x: x > 327,
        'end_frame': lambda x: x < 1327
    })
    .events.df

And the resulting :obj:`DataFrame` looks like this:

=======     ==========  =========== =========   =========
(index)     event_type  start_frame end_frame   player_id
=======     ==========  =========== =========   =========
0           pass        1           424         79
1           goal        425         599         79
2           pass        600         944         19
3           pass        945         1099        2
4           pass        1100        1279        3
=======     ==========  =========== =========   =========
