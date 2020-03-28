:meth:`expand_to_match_ds`: A closer look.
******************************************

In this section we shall take a closer look at the internals of
:meth:`expand_to_match_ds`. This method transforms a :obj:`DataFrame` into a
a :obj:`DataArray` by performing a series of operations to it.

Recall from :doc:`its signature <../api_reference/expand_to_match_ds>` that
the arguments it takes are:

-   :attr:`dimension_matching_col`
-   :attr:`fill_method`
-   :attr:`fill_value_col`

The transformation occurs essentially with the following code snippet: ::

    return xr.DataArray(
        self.df
        .sort_values(dimension_matching_col)
        .reset_index()
        .rename(columns={'index': fill_value_col}, errors='ignore')
        .set_index(dimension_matching_col, drop=False)
        [fill_value_col]
        .reindex(
            self._ds[self._get_ds_from_df(dimension_matching_col)],
            method=fill_method
        )
    )

Continuing with the
:doc:`tutorial <../tutorials/sports_data/expand_to_match_ds>`, let's
see how the original :obj:`DataFrame` is progressively transformed.

0.  This is the original :obj:`DataFrame`.

=======     ==========  =========== =========   =========
(index)     event_type  start_frame end_frame   player_id
=======     ==========  =========== =========   =========
0           pass        1           424         79
1           goal        425         599         79
2           pass        600         944         19
3           pass        945         1099        2
4           pass        1100        1279        3
5           penalty     1280        1889        2
6           goal        1890        2019        3
7           pass        2020        2299        79
8           pass        2300        2389        2
9           penalty     2390        2450        79
=======     ==========  =========== =========   =========

1.  The :obj:`DataFrame` gets sorted on the column
    :attr:`dimension_matching_col`, which is :attr:`start_frame` in this case. ::

        .sort_values(dimension_matching_col)

It is already sorted, so nothing changes.

2.  The index of the :obj:`DataFrame` gets reset. ::

        .reset_index()

=   ======= ==========  =========== =========   =========
.   (index) event_type  start_frame end_frame   player_id
=   ======= ==========  =========== =========   =========
0   0       pass        1           424         79
1   1       goal        425         599         79
2   2       pass        600         944         19
3   3       pass        945         1099        2
4   4       pass        1100        1279        3
5   5       penalty     1280        1889        2
6   6       goal        1890        2019        3
7   7       pass        2020        2299        79
8   8       pass        2300        2389        2
9   9       penalty     2390        2450        79
=   ======= ==========  =========== =========   =========

Now **(index)** is a column of its own.

3.  The column **(index)** gets renamed to :attr:`fill_value_col`, which is
    :attr:`event_index` in this case: ::

        .rename(columns={'index': fill_value_col}, errors='ignore')

=   =========== ==========  =========== =========   =========
.   event_index event_type  start_frame end_frame   player_id
=   =========== ==========  =========== =========   =========
0   0           pass        1           424         79
1   1           goal        425         599         79
2   2           pass        600         944         19
3   3           pass        945         1099        2
4   4           pass        1100        1279        3
5   5           penalty     1280        1889        2
6   6           goal        1890        2019        3
7   7           pass        2020        2299        79
8   8           pass        2300        2389        2
9   9           penalty     2390        2450        79
=   =========== ==========  =========== =========   =========

4.  The column :attr:`dimension_matching_col` is set as the new index of the
    :obj:`DataFrame`: ::

        .set_index(dimension_matching_col, drop=False)

=========== =========== ==========  =========== =========   =========
start_frame event_index event_type  start_frame end_frame   player_id
=========== =========== ==========  =========== =========   =========
1           0           pass        1           424         79
425         1           goal        425         599         79
600         2           pass        600         944         19
945         3           pass        945         1099        2
1100        4           pass        1100        1279        3
1280        5           penalty     1280        1889        2
1890        6           goal        1890        2019        3
2020        7           pass        2020        2299        79
2300        8           pass        2300        2389        2
2390        9           penalty     2390        2450        79
=========== =========== ==========  =========== =========   =========

5.  All columns of the :obj:`DataFrame` except for :attr:`fill_value_col`,
    which is :attr:`event_index` in this case, and the index are dropped. ::

        [fill_value_col]

=========== =
start_frame .
=========== =
1           0
425         1
600         2
945         3
1100        4
1280        5
1890        6
2020        7
2300        8
2390        9
=========== =

6.  The :obj:`DataFrame` is now reindexed to the :obj:`Dataset` coordinate or
    dimension that matches :attr:`dimension_matching_col`, which is
    :attr:`frame` in this case. ::

        .reindex(
            self._ds[self._get_ds_from_df(dimension_matching_col)],
            method=fill_method
        )

====== ===
frame  .
====== ===
1      0.0
...    ...
425    1.0
...    ...
600    2.0
...    ...
945    3.0
...    ...
1100   4.0
...    ...
1280   5.0
...    ...
1890   6.0
...    ...
2020   7.0
...    ...
2300   8.0
...    ...
2390   9.0
====== ===

All the missing data in the nameless column that's left in the :obj:`DataFrame`
is :obj:`NaN`.

7.  The :obj:`DataFrame` is finally converted into a :obj:`DataArray`. ::

        return xr.DataArray(
            ...
        )

::

    <xarray.DataArray 'event_index' (frame: 2450)>
    array([ 0., nan, nan, ..., nan, nan, nan])
    Coordinates:
    * frame    (frame) int64 1 2 3 4 5 6 7 ... 2444 2445 2446 2447 2448 2449 2450

This :obj:`DataArray` is useful on its own because it allows us to see which
values of the :obj:`Dataset` coordinate or dimension match with unique events.
It is also used to group the :obj:`Dataset` in :meth:`groupby_events`.
