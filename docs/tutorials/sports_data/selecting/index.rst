Selecting
*********

We now move on to the most popular action in :mod:`xarray`: selection. Here is
where we start grasping the benefits of :mod:`xarray-events`. The method
provided by :mod:`xarray` is very powerful and useful when we need to perform
selections on a :obj:`Dataset` only. However, the extended
:meth:`~.xarray_events.EventsAccessor.sel` in :mod:`xarray-events` allows you to
make selections that also take into account the existence of events data.

.. toctree::
    :titlesonly:

    events_only/index
    dataset_only
    everything
