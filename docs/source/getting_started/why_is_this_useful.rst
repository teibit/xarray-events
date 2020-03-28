Why is this useful?
*******************

The need for this API arises when you decide to represent events related to the
data in a :obj:`Dataset`.

A possible approach would be to have two separate :obj:`Dataset` objects: one
for the actual data and another one for the events data. However, this way of
managing the two lacks structure and is inflexible because the two entities
aren't actually connected in any way.

This API uses a slightly more clever approach by storing the events data
directly inside the :obj:`Dataset` as a private attribute. Both data sources now
coexist and are inherently linked together. This organization enables the use of
an Python accessors that may add functionality while having both data sources
handy. This is precisely the way we've constructed this: :mod:`xarray-events` is
simply a :obj:`Dataset` accessor that builds functionality on top of the base
class.
