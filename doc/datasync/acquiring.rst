Acquiring subscriptions
=======================

In order to acquire the subscriptions in the browser clients and handle the updates, Snorky.js provides a DataSync connector.

Basic usage
~~~~~~~~~~~

The DataSync service usage is very simple, just tell :js:class:`Snorky` that you need a :js:class:`Snorky.DataSync` service.

.. code-block:: javascript

    var snorky = new Snorky(WebSocket, "ws://localhost:8001/ws", {
      "datasync": Snorky.DataSync
    });

.. js:class:: Snorky.DataSync

    DataSync service connector.

    **Events**

    .. js:attribute:: deltaReceived

        Event raised when a delta arrives.

        The event is dispatched with the delta as argument, being it a dictionary with the following fields:

            .. js:attribute:: model

                The model class over the change occurred.

            .. js:attribute:: type

                The type of the delta. Will be either ``"insert"``, ``"update"`` or ``"delete"``.

            .. js:attribute:: data

                The element added or removed. Only in ``insert`` and ``delete`` deltas.

            .. js:attribute:: oldData

                The element before the update. Only in ``update`` deltas.

            .. js:attribute:: newData

                The element after the update. Only in ``update`` deltas.

You can bind the :js:attr:`deltaReceived` event and process the deltas as required by your application.

.. code-block:: javascript

    snorky.services.datasync.deltaReceived.add(
      function (delta) {
        if (delta.type == "insert") {
          /* code for insertions */
        } else if (delta.type == "update") {
          /* code for updates */
        } else if (delta.type == "delete") {
          /* code for deletions */
        }
      });
