Constraints that match everything
+++++++++++++++++++++++++++++++++

Let's now see how we put together all of the functionality of our accessor to
make useful (though complex) queries.

Given that now :meth:`sel` considers two different search spaces (i.e. the
events :obj:`DataFrame` and the :obj:`Dataset`), we can make the search be so
complex that it searches in both spaces. This is a powerful feature of our
accessor.

Say we may wish to perform a selection with the following specification:

-   An event of type *pass*.
-   The frames are within 1728 and 2378.

Moreover, we want the result to be consistent across the :obj:`Dataset` and the
events :obj:`DataFrame`. In that case, we can achieve this like this:

.. jupyter-execute:: ../raw_data.py
    :hide-code:

.. jupyter-execute::

    (
        ds
        .events.load(events, {'frame': ('start_frame', 'end_frame')})
        .events.sel(
            {
                'frame': range(1729, 2378),
                'start_frame': lambda frame: frame > 1728,
                'end_frame': lambda frame: frame < 2378,
                'event_type': 'pass'
            }
        )
    )

Internally, :meth:`sel` filters the events :obj:`DataFrame` and also the
:obj:`Dataset`, each with its corresponding attributes.

The resulting :obj:`DataFrame` looks like this:

.. jupyter-execute::

    ds.events.df

We want to emphasize how we give the user the power to do things exactly as they
want them since the constraints have to be properly specified for both the
:obj:`Dataset` and also the :obj:`DataFrame`. :meth:`sel` does not assume that
they may want to select both or anything like that. It all must be specified.
This provides great flexibility.
