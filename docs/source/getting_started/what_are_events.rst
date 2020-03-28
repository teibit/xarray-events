What are events?
****************

In this section we shall provide a description of what events are.

:mod:`xarray`
+++++++++++++

This library is based on :mod:`xarray`. As such, we encourage you to first
become familiar with it before continuing with this guide. `Their official
documentation <http://xarray.pydata.org/>`_ does already a fantastic job at
explaining in detail every aspect of their approach on managing data.

Concept
+++++++

Now that you're familiar with :mod:`xarray`, let's describe what we mean by
events.

`The dictionary definition <https://www.merriam-webster.com/dictionary/event>`_
goes along the lines of the occurrence of something. Ours doesn't deviate much
from this. Depending on the kind of data that the :obj:`Dataset` stores,
events can be seen as occurrences of systematic processes that share the same
characteristics of the data. Hence, we expect the attributes or dimensions of
an event to be shared to some extent with the dimensions of the data described
by the :obj:`Dataset`.
