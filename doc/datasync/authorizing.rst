Authorizing subscriptions
=========================

In order to maintain the system secure and to avoid race conditions, browser clients cannot directly ask for subscriptions to Snorky. Instead, they need to ask to another party, usually your web application, to fetch the data and authorize a subscription.

The subscription process
~~~~~~~~~~~~~~~~~~~~~~~~

1. The browser client requests both the current data and a subscription. This can be done in a RESTful way with the header ``X-Snorky``.

2. The web application sends to Snorky a subscription authorization request to one or more dealers. The web application receives a *subscription token* in return.

3. The web application queries the database.

4. The web application sends to the client both the data and the subscription token.

5. The browser client shows the received data on the user interface, connects to Snorky and sends it the subscription token in order to receive updates.

The authorization request
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: snorky.services.datasync

    :py:class:`DataSyncBackend` provides the RPC command :py:func:`DataSyncBackend.authorizeSubscription` to request a subscription token.

    .. automethod:: DataSyncBackend.authorizeSubscription

.. warning::

    In order to avoid race conditions, the database query must not be made until the subscription token has been received.

Snorky headers
~~~~~~~~~~~~~~

The subscription mechanism fits well into RESTful APIs. The recommended way to do this is with additional headers.

When a client wants to get both certain data and a subscription to updates in that data, it must send a header ``X-Snorky: Subscribe``.

When the server detects this header it must check client permissions and, if it is allowed to do so, it will ask Snorky for a subscription token for the kind of data requested.

For example, if the client requested the comments for the blog post with id 15, it will put in the subscription the dealer ``CommentsByBlogEntry`` with query ``15``.

Once received the token, the server will send it to the client in the response header ``X-Subscription``.

The server will query the database for the current comments in the blog entry ``15`` and write them in the response body.

Note this protocol is merely conventional. You can use whatever protocol you want to ask for subscriptions and return them later.
