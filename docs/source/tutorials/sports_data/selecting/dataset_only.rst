Constraints that match only the :obj:`Dataset`
++++++++++++++++++++++++++++++++++++++++++++++

We may also perform a regular selection on the :obj:`Dataset` as we would
without this accessor. In that case, :meth:`sel` works just as it does on
:mod:`xarray`. Although we support this functionality, it's simpler to just
stick to the :mod:`xarray` method.

.. Note::

    We also support the regular method arguments of the :meth:`sel` in
    :mod:`xarray`.
