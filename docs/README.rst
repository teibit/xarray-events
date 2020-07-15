.. image:: https://codecov.io/gh/teibit/xarray-events/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/teibit/xarray-events
    :alt: Code Coverage Status (Codecov)

.. image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :target: https://xarray-events.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status (RTFD)

.. image:: https://travis-ci.com/teibit/xarray-events.svg?branch=master
    :target: https://travis-ci.com/teibit/xarray-events
    :alt: Build Status (Travis CI)

.. image:: https://img.shields.io/github/license/teibit/xarray-events
    :target: https://github.com/teibit/xarray-events/blob/master/LICENSE.txt
    :alt: License

.. image:: https://img.shields.io/pypi/v/xarray-events
    :target: https://pypi.org/project/xarray-events/
    :alt: PyPI

.. image:: https://img.shields.io/pypi/dm/xarray-events
    :target: https://pypi.org/project/xarray-events/
    :alt: PyPI - Downloads

xarray-events: An open-source extension of xarray that supports events handling
*******************************************************************************

**xarray-events** is an open-source API based on **xarray**. It provides
sophisticated mechanisms to handle *events* easily.

Events data is something very natural to conceive, yet it's rather infrequent to
see native support for it in common data analysis libraries. Our aim is to fill
this gap in a very general way, so that scientists from any domain can take
benefit from this. We're building all of this on top of **xarray** because
this is already a well-established open-source library that provides exciting
new ways of handling multi-dimensional labelled data, with applications in a
wide range of domains of science.

This library makes it possible to *extend* a **Dataset** by introducing
events based on the data. Internally it works as an *accessor* to **xarray**
that provides new methods to deal with new data in the form of events and also
extends the existing ones already provided by it to add compatibility with this
new kind of data.

We hope that this project inspires you to rethink how you currently handle data
and, if needed, improve it.

Example
+++++++

Assume we have a **DataFrame** (in a variable called **events**) of events and a
**Dataset** (in a variable called **ds**) of sports data in such a way that
the events are a meaningful addition to the data stored in the **Dataset**.

.. code-block:: python

    events = pd.DataFrame(
        {
            'event_type': ['pass', 'goal', 'pass', 'pass'],
            'start_frame': [1, 175, 251, 376],
            'end_frame': [174, 250, 375, 500]
        }
    )

    ds = xr.Dataset(
        data_vars={
            'ball_trajectory': (
                ['frame', 'cartesian_coords'],
                np.exp(np.linspace((-6, -8), (3, 2), 500))
            )
        },
        coords={'frame': np.arange(1, 501), 'cartesian_coords': ['x', 'y']},
        attrs={'match_id': 12, 'resolution_fps': 25, '_events': events}
    )

With this API we can do the following:

.. code-block:: python

    ds
    .events.load(events, {'frame': ('start_frame', 'end_frame')})
    .events.sel({
        'frame': range(175, 376),
        'start_frame': lambda frame: frame >= 175,
        'end_frame': lambda frame: frame < 376
    })
    .events.groupby_events('ball_trajectory')
    .mean()

This will:

-   Load the events DataFrame specifying that the columns `start_frame` and
    `end_frame` define the span of the events as per the Dataset's coordinate
    `frame`.

-   Perform a selection constraining the frames to be only in the range
    [175, 375].

-   Group the **DataVariable** `ball_trajectory` by the events.

-   Compute the *mean* of each group.

.. code-block:: python

    <xarray.DataArray 'ball_trajectory' (event_index: 2, cartesian_coords: 2)>
    array([[0.12144595, 0.02556095],
           [0.84426861, 0.22346441]])
    Coordinates:
      * cartesian_coords  (cartesian_coords) <U1 'x' 'y'
      * event_index       (event_index) int64 1 2

This result can be interpreted as the mean 2D position of the ball over the span
of each event during the frames [175, 375]. This is a very powerful set of
operations performed via some simple and intuitive function calls. This is the
beauty of this API.
