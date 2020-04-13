:meth:`expand_to_match_ds`: A closer look.
******************************************

In this section we shall take a closer look at the internals of
:meth:`expand_to_match_ds`. This method transforms a :obj:`DataFrame` into a
:obj:`DataArray` by performing a series of operations to it.

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

.. jupyter-execute:: ../tutorials/sports_data/raw_data.py
    :hide-code:

.. jupyter-execute::
    :hide-code:
    :hide-output:

    (
        ds
        .events.load(events, {'frame': ('start_frame', 'end_frame')})
        .events.expand_to_match_ds('start_frame')
    )

.. jupyter-execute::

    ds.events.df

1.  The :obj:`DataFrame` gets sorted on the column
    :attr:`dimension_matching_col`, which is :attr:`start_frame` in this case. ::

        .sort_values(dimension_matching_col)

It is already sorted, so nothing changes.

2.  The index of the :obj:`DataFrame` gets reset. ::

        .reset_index()

.. jupyter-execute::
    :hide-code:

    (
        ds.events.df
        .sort_values('start_frame')
        .reset_index()
    )

Now **index** is a column of its own.

3.  The column **index** gets renamed to :attr:`fill_value_col`, which is
    :attr:`event_index` in this case: ::

        .rename(columns={'index': fill_value_col}, errors='ignore')

.. jupyter-execute::
    :hide-code:

    (
        ds.events.df
        .sort_values('start_frame')
        .reset_index()
        .rename(columns={'index': 'event_index'}, errors='ignore')
    )

4.  The column :attr:`dimension_matching_col` is set as the new index of the
    :obj:`DataFrame`: ::

        .set_index(dimension_matching_col, drop=False)

.. jupyter-execute::
    :hide-code:

    (
        ds.events.df
        .sort_values('start_frame')
        .reset_index()
        .rename(columns={'index': 'event_index'}, errors='ignore')
        .set_index('start_frame', drop=False)
    )

5.  All columns of the :obj:`DataFrame` except for :attr:`fill_value_col`,
    which is :attr:`event_index` in this case, and the index are dropped. ::

        [fill_value_col]

.. jupyter-execute::
    :hide-code:

    (
        ds.events.df
        .sort_values('start_frame')
        .reset_index()
        .rename(columns={'index': 'event_index'}, errors='ignore')
        .set_index('start_frame', drop=False)
        ['event_index']
    )

6.  The :obj:`DataFrame` is now reindexed to the :obj:`Dataset` coordinate or
    dimension that matches :attr:`dimension_matching_col`, which is
    :attr:`frame` in this case. Notice that there's **no fill method**. ::

        .reindex(
            self._ds[ds.events._get_ds_from_df(dimension_matching_col)],
            method=fill_method
        )

.. jupyter-execute::
    :hide-code:

    (
        ds.events.df
        .sort_values('start_frame')
        .reset_index()
        .rename(columns={'index': 'event_index'}, errors='ignore')
        .set_index('start_frame', drop=False)
        ['event_index']
        .reindex(
            ds.events._ds[ds.events._get_ds_from_df('start_frame')]
        )
    )

7.  The :obj:`DataFrame` is finally converted into a :obj:`DataArray`. ::

        return xr.DataArray(
            ...
        )

.. jupyter-execute::
    :hide-code:

    xr.DataArray(
        ds.events.df
        .sort_values('start_frame')
        .reset_index()
        .rename(columns={'index': 'event_index'}, errors='ignore')
        .set_index('start_frame', drop=False)
        ['event_index']
        .reindex(
            ds.events._ds[ds.events._get_ds_from_df('start_frame')]
        )
    )

This :obj:`DataArray` is useful on its own because it allows us to see which
values of the :obj:`Dataset` coordinate or dimension match with unique events.
It is also used to group the :obj:`Dataset` in :meth:`groupby_events`.
