Constraints that specify *lambda functions*
*******************************************

Selecting ranges in the events :obj:`DataFrame` is possible. We provide support
for lambda functions in order to empower the user to specify arbitrary
conditions. In the example below we're going to use a simple condition but,
evidently, it can be as complex as needed.

Say we want to select all events that occurred between frames 327 and 1327. We
can do it like this:

.. jupyter-execute:: ../../raw_data.py
    :hide-code:

.. jupyter-execute::

    (
        ds
        .events.load(events, {'frame': ('start_frame', 'end_frame')})
        .events.sel(
            {
                'start_frame': lambda frame: frame > 327,
                'end_frame': lambda frame: frame < 1327
            }
        )
        .events.df
    )
