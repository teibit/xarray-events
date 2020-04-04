Known limitations
*****************

While we consider :mod:`xarray-events` to be useful for some specific use cases,
we do also recognize that it still has a lot of room for improvement. This
library is meant to be applicable to a wide range of areas, so we have attempted
to maintain generality in mind while developing it all along.

In this section we detail some known limitations of this library.

Custom-type duration values
+++++++++++++++++++++++++++

**Tracking bug**: https://github.com/teibit/xarray-events/issues/2

The values of the events :obj:`DataFrame` on the columns that specify a duration
should be integers. This means that they must not be custom objects. This is
worth mentioning because one might want them to be *Timestamp* objects (from
:mod:`Pandas`), for example, but this is not possible because comparison between
them isn't well implemented. This limitation isn't impactful until one starts
using :meth:`groupby_events` because of :meth:`df_contains_overlapping_events`.
