Raw data
********

:obj:`Dataset`
++++++++++++++

We're going to work with a :obj:`Dataset` that describes a football match
consisting of the following:

-   The following two coordinates:

    -   The *frame* at which the ball is at. There are 250 possible frames in
        this recording.
    -   The *cartesian coordinates* (x,y) of the ball's position.

-   A :obj:`DataVariable` that describes the *trajectory* of the ball. It is
    described by the two coordinates of the :obj:`Dataset`.

-   The following two attributes:

    -   The match ID, which is 12.
    -   The resolution (25 Hz) of the recording in frames per second.

Events
++++++

We're going to create events directly in a :obj:`DataFrame` consisting of the
following attributes:

-   The event *type*, which can be: penalty, pass or goal.

-   The frame where the event starts.

-   The frame where the event ends.

-   The ID of the responsible player.

Code
++++

<script type="text/x-thebe-config">
{
    requestKernel: true,
    binderOptions: {
        repo: "xarray-events/docs/requirements",
        ref: "master",
    },
    kernelOptions: {
      kernelName: "python3",
    },
    codeMirrorConfig: {
        theme: "default"
    }
}
</script>

The described dataset can be built as follows:

.. jupyter-execute:: raw_data.py

The new :obj:`Dataset` looks like this:

.. jupyter-execute::

    ds

And the new :obj:`DataFrame` looks like this:

.. jupyter-execute::

    events
