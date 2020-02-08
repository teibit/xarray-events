[![codecov](https://codecov.io/gh/teibit/xarray-events/branch/master/graph/badge.svg)](https://codecov.io/gh/teibit/xarray-events)
[![Build Status](https://travis-ci.com/teibit/xarray-events.svg?branch=master)](https://travis-ci.com/teibit/xarray-events)

xarray-events: An open-source extension of xarray that supports events handling
*******************************************************************************

.. toctree::
    :titlesonly:
    :hidden:

    getting_started/index
    tutorials/index
    api_reference/index
    contact

:mod:`xarray-events` is an open-source API based on :mod:`xarray`. It provides
sophisticated mechanisms to handle *events* easily.

Events data is something very natural to conceive, yet it's rather infrequent to
see native support for it in common data analysis libraries. Our aim is to fill
this gap in a very general way, so that scientists from any domain can take
benefit from this. We're building all of this on top of :mod:`xarray` because
this is already a well-established open-source library that provides exciting
new ways of handling multi-dimensional labelled data, with applications in a
wide range of domains of science.

This library makes it possible to *extend* a :obj:`Dataset` by introducing
events based on the data. Internally it works as an *accessor* to :mod:`xarray`
that provides new methods to deal with new data in the form of events and also
extends the existing ones already provided by it to add compatibility with this
new kind of data.

We hope that this project inspires you to rethink how you currently handle data
and, if needed, improve it.

Licence
+++++++
