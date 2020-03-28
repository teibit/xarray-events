Constraints that specify collections
************************************

Selecting in the events :obj:`DataFrame` by the values in any arbitrary
:mod:`Collection` is possible. The usefulness of this possibility becomes more
evident when there is a complex process behind obtaining such a collection. For
the sake of an example, let's assume such a collection is already given.

Say we want to select all events where the player is in some specified list. We
can do it like this:

.. jupyter-execute:: ../../raw_data.py
    :hide-code:

.. jupyter-execute::

    (
        ds
        .events.load(events, {'frame': ('start_frame', 'end_frame')})
        .events.sel({'player_id': [2, 3]})
        .events.df
    )
