Sending change notifications
============================

Change notifications, also called *deltas*, must be sent to Snorky for each change that may be subscripted by a user.

These notifications must be sent to the :py:class:`snorky.services.datasync.DataSyncBackend` service, which must be connected to a :py:class:`snorky.services.datasync.DataSyncService`.

The services will be explained later in more detail, but for now, this is how they could be added to a Snorky server.

.. literalinclude:: /examples/incomplete_datasync.py

Delta types
~~~~~~~~~~~

There are three delta types:

* **Insertion**: A new element of the model class, e.g. a row, was created.

* **Update**: An already existing element was changed, e.g. a row was edited.

* **Delete**: An element was removed.

Sending deltas
~~~~~~~~~~~~~~

.. automodule:: snorky.services.datasync

    In order to send one or more deltas, an RPC call to ``publishDeltas`` must be made.

    .. automethod:: DataSyncBackend.publishDeltas


Each delta dictionary must have the following fields:

* ``type``: It must be ``"insert"``, ``"update"`` or ``"delete"``, depending on the nature of the change.

* ``model``: A name for the model class, e.g. the table name. Different data kinds with different fields should have different values for this property.

* If the delta is an insertion or deletion delta:

  * ``data``: The object created or removed, encoded as a JSON entity. It must contain all the fields that may be required to be displayed by the end application.

* If the delta in an update delta:

  * ``newData``: The object as a JSON object, after the update was made. It must contain all the fields that may be required to be displayed by the end application.

  * ``oldData``: The object as a JSON object, before the update was made. It must contain at least enough fields to identify the element that was updated.

    If the model can be subscripted filtered by some fields, the fields used as filter must also be present in order for Snorky to be able to know whether the matched the filters before and after the update.

When to send deltas
~~~~~~~~~~~~~~~~~~~

Deltas must be sent after the database has been modified. If several changes are being made in an atomic transaction, it's advised not to send the deltas until the transaction has been committed.

Example
~~~~~~~

The following code sends an insertion delta using the Snorky Python backend connector.

.. code:: python

    from snorky.backend import SnorkyBackend, SnorkyHTTPTransport, SnorkyError

    backend_http = SnorkyHTTPTransport("http://localhost:8001/backend",
                                       key="swordfish")
    backend = SnorkyBackend(backend_http)

    backend.call("datasync_backend", "publish", deltas=[{
        "type": "insert",
        "model": "Task",
        "data": {
            "title": "Send a delta",
            "completed": true
        }
    }])
