Choosing dealers
================

Once Snorky receives all relevant deltas, the next step is to re-send them to the interested clients, if any. This is controlled with dealer classes.

What is a dealer
~~~~~~~~~~~~~~~~

Dealers are classes which track client subscriptions to certain kinds of models.

Dealers also manage the delivery of deltas, by determining which clients are subscripted to the information that they carry.

What is a subscription
~~~~~~~~~~~~~~~~~~~~~~

In Snorky, clients acquire *subscriptions* to dealers. Each subscription conforms one or more *subscription items*. Each *subscription item* specifies a dealer, and a query to that dealer.

For example, a dealer may be called ``CommentsByBlogEntry``. A subscription may contain one subscription item having ``CommentsByBlogEntry`` as dealer and ``15`` as query, in order to get notified of new comments in the blog entry with id 15.

The Dealer API
~~~~~~~~~~~~~~

.. automodule:: snorky.services.datasync.dealers

    The most basic dealer API is the :py:class:`Dealer` class. You can subclass it to make new dealers.

    .. autoclass:: Dealer

        .. autoattribute:: name
        .. autoattribute:: model
        .. automethod:: add_subscription_item
        .. automethod:: remove_subscription_item
        .. automethod:: get_subscription_items_for_model

Simple dealers
~~~~~~~~~~~~~~

Often your dealer only has to filter models by a certain field which clients subscribe to.

For example, the ``CommentsByBlogEntry`` dealer would receive subscriptions that specify a blog entry id as query, and each time it receives a delta of model ``Comment``, it would look which blog entry id it is for, and forward it to those clients which subscripted to it.

.. automodule:: snorky.services.datasync.dealers

    Snorky comes with a :py:class:`SimpleDealer` class that leverages this pattern.

    .. autoclass:: SimpleDealer

        .. automethod:: get_key_for_model

Example
-------

.. code:: python

    from snorky.services.datasync.dealers import SimpleDealer

    class CommentsByBlogEntry(SimpleDealer):
        name = "CommentsByBlogEntry" # optional
        model = "Comment"

        def get_key_for_model(self, model):
            return model["entryId"]

Broadcast dealers
~~~~~~~~~~~~~~~~~

.. automodule:: snorky.services.datasync.dealers

    Sometimes you want the clients to receive all deltas for a certain model class, unfiltered. For this purpose there is the :py:class:`BroadcastDealer` class.

    .. autoclass:: BroadcastDealer

Example
-------

.. code:: python

    from snorky.services.datasync.dealers import BroadcastDealer

    class AllTasks(BroadcastDealer):
        name = "AllTasks" # optional
        model = "Task"

Filter dealers
~~~~~~~~~~~~~~

.. automodule:: snorky.services.datasync.dealers

    For cases where clients need to ask for data filtered to complex criteria :py:class:`FilterDealer` provides an advanced dealer which supports complex filter expressions.

Filter syntax
-------------

The subscription query for this dealer must be a JSON list specifying a filter expression in prefix notation. These are some examples:

* ``['==', 'color', 'blue']``

  *color* is 'blue'.

* ``['<', 'age', 21]``

  *age* is less than 21.

* ``['>=', 'age', 21]``

  *age* is greater than or equal to 21.

* ``['and', ['==', 'service', 'prosody'], ['>=', 'severity_level', 3]]``

  *service* is 'prosody' and *severity_level* is greater than or equal to 3.

* ``['or', ['not', ['==', 'service', 'java']], ['>=', 'severity_level', 3]]``

  *service* is not 'java' or *severity_level* is greater than or equal to 3.

* ``['==', 'player.color', 'blue']``

  *player* is a dictionary which contains a property ``color``, and the value of that property is 'blue'.

Example
-------

.. code:: python

    from snorky.services.datasync.dealers import BroadcastDealer

    class FilteredTasks(FilterDealer):
        name = "FilteredTasks" # optional
        model = "Task"
