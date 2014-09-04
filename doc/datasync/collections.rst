Updating collections
====================

Often an integral part of the delta processing is modifying a collection stored in JS, e.g. in an array. This is specially true if you use a MV* framework like AngularJS.

For example, you may store the initially received elements in an array and later modify it as deltas come from Snorky.

In order to leverage this pattern there is the :js:class:`Snorky.DataSync.CollectionDeltaProcessor` class.

.. js:class:: Snorky.DataSync.CollectionDeltaProcessor(collections, options)

    Updates one or more collections with deltas received from Snorky.

    :param Object collections: A dictionary where each key is a model class name and each value is a collection.

    :param Object options: An optional dictionary with additional options.

        .. js:attribute:: itemsAreEqual

            Provides a custom item comparison (see below).

    .. js:function:: itemsAreEqual(item, other, delta)

        If return true, two items from a collection will be considered the same. This function is used for processing update and deletion deltas.

        The updated or deleted element will be the one that makes this function returns true when compared with the element in the delta.

        By default compares the ``id`` field in both ``item`` and ``other`` and returns true if they are equal.

    .. js:function:: processDelta(delta)

        Checks if the delta is associated with any registered collection. If it is, updates the collection adding, updating or removing the matching element.

Collections
~~~~~~~~~~~

A *collection*, as understood by :js:class:`Snorky.DataSync.CollectionDeltaProcessor` is a class which allows inserting methods and getting an iterator with update and delete capabilities.

.. js:class:: Snorky.DataSync.Collection

    An abstract interface for a collection.

    .. js:function:: insert(value)

        Inserts a new element in the collection.

    .. js:function:: getIterator()

        Returns an iterator to the collection.

.. js:class:: Snorky.DataSync.Iterator

    An abstract interface for an iterator.

    .. js:function:: next()

        Advances the iterator to the next element and returns it.

        This method should also be called to retrieve the first element in the collection.

    .. js:function:: hasNext()

        True if there are elements in the collection which the iterator has not explored.

    .. js:function:: remove()

        Remove the last element returned by :js:func:`next()` from the collection.

    .. js:function:: update(newValue)

        Replace the last element returned by :js:func:`next()` with the value provided as argument.

Array collection
~~~~~~~~~~~~~~~~

The most common collection is the one that is backend by a JavaScript array.

.. js:class:: Snorky.DataSync.ArrayCollection(array, options)

    :param Array array: An array, to which this class will expose a collection interface.

    :param Object options: An optional dictionary of options:

        .. js:attribute:: transformItem

            When an element is inserted or updated, this function will be called with the element to insert or update, and the object returned will be inserted or updated instead.

            This is often used when you use *fat models*, that is, you extend the JSON objects that you receive from the server in order to provide helper methods that calculate additional data or perform special operations.

            This function gives you the opportunity to add additional methods or perform transformations in the models received from Snorky.

Single item collection
~~~~~~~~~~~~~~~~~~~~~~

Sometimes the data you synchronize with Snorky is not a list but a single element. :js:class:`Snorky.DataSync.SingleItemCollection` allows you to update it by providing an update callback.

.. js:class:: Snorky.DataSync.SingleItemCollection(readHandler, updateHandler, removeHandler)

    Virtual collection of a single item.

    :param function readHandler: Called to get the current item value.

    :param function updateHandler: Called to update the item value.

    :param function removeHandler: Optional, called when the item is deleted.

Example usage
~~~~~~~~~~~~~

The following code would update the array ``comments`` with the deltas received from Snorky.

.. code-block:: javascript

    var collectionProcessor = new Snorky.DataSync.CollectionDeltaProcessor({
      "Comment": new Snorky.DataSync.ArrayCollection(comments)
    });

    // Delegate delta processing to the collection processor
    snorky.services.datasync.deltaReceived.add(function(delta) {
      collectionProcessor.processDelta(delta);
    });
