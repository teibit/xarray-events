Constraints that specify collections
************************************

Selecting in the events :obj:`DataFrame` by the values in any arbitrary
:mod:`Collection` is possible. The usefulness of this possibility becomes more
evident when there is a complex process behind obtaining such a collection. For
the sake of an example, let's assume such a collection is already given.

Say we want to select all events where the player is in some specified list. We
can do it like this: ::

    ds
    .events.sel({'player_id': [2, 3]})
    .events.df

And the resulting :obj:`DataFrame` looks like this:

=======     ==========  =========== =========   =========
(index)     event_type  start_frame end_frame   player_id
=======     ==========  =========== =========   =========
3           pass        945         1099        2
4           pass        1100        1279        3
5           penalty     1280        1889        2
6           goal        1890        2019        3
8           pass        2300        2389        2
=======     ==========  =========== =========   =========
