Overview of Snorky
==================

The following is an example server with Snorky exposing a simple Pub Sub service. The goal of this section is to explain each of the parts involved on it, both from Snorky and from Tornado.

.. code:: python

    import os
    from tornado.ioloop import IOLoop
    from tornado.web import Application
    from snorky import ServiceRegistry

    from snorky.request_handlers.websocket import SnorkyWebSocketHandler
    from snorky.services.pubsub import PubSubService

    if __name__ == "__main__":
        service_registry = ServiceRegistry()
        service_registry.register_service(PubSubService("messaging"))

        application = Application([
            SnorkyWebSocketHandler.get_route(service_registry, "/ws"),
        ])
        application.listen(8002, address="")

        try:
            print("Snorky running...")
            IOLoop.instance().start()
        except KeyboardInterrupt:
            pass

The I/O loop
~~~~~~~~~~~~

:py:class:`tornado.ioloop.IOLoop` is the Tornado event loop. Being an asynchronous server, there are no separate threads for each connection. Instead, all sockets are managed by this class.

``IOLoop`` performs and endless loop in which tells the operating system to notify it of any event occurred in the managed sockets and in turn dispatches the event to the class that owns the socket. This loop starts when ``IOLoop.instance().start()`` is called.

``IOLoop`` is a singleton class. In normal usage you even don't need to keep references to it, the framework manages this automatically. Most of the times you only need call ``IOLoop.instance().start()`` and go on.

Services
~~~~~~~~

Services are classes which process messages. Messages are JSON entities, that is: they can be any data type representable with JSON, like strings, arrays (also called *lists*) or objects (also called *dictionaries*). Services often are stateful and track client connections.

Seen in the heading example, :py:class:`snorky.services.pubsub.PubSubService` is a service which accepts several methods: ``join``, ``leave`` and ``publish``. Clients can connect to the server and ask ``PubSubService`` to join them to a certain *channel* (which is also JSON entity, typically a string). An user can send a ``publish`` command to a channel which would trigger notifications in all those clients which joined that channel.

``PubSubService`` is a simple service which can be useful in a number of situations, but often you will also write your own services, either from scratch or subclassing other services. :doc:`services` explains this in detail.

Service registries
~~~~~~~~~~~~~~~~~~

The ``ServiceRegistry`` class tracks a fixed number of services, each identified with a name, which should be a string.

``ServiceRegistry`` is also responsible for delivery of messages to its services. There can be several instances tracking different services at the same time.

:doc:`backend` explains how this can be used to offer both a *public* set of services on an interface, and a *private* one in other, often firewalled. This can be used for example to only allow a trusted machine to send certain types of events to the clients subscribed to the public services.

Request handlers
~~~~~~~~~~~~~~~~

Request handlers are Tornado classes which are intended to respond to HTTP and WebSocket requests. They inherit from :py:class:`tornado.web.RequestHandler` and they are explained in detail in the Tornado documentation.

Snorky request handlers are associated with a service registry. Their job is to receive messages from the outside and forward them to the service registry, providing also the service with means to send messages in the other way.

Several request handlers can be attached to the same service registry or to independent registries.

Currently there are three request handlers bundled with Snorky:

 * :py:class:`snorky.request_handlers.websocket.SnorkyWebSocketHandler`: Handles WebSocket connections.

 * :py:class:`snorky.request_handlers.sockjs.SnorkySockJSHandler`: Handles SockJS connections, which are an abstraction layer of WebSocket providing fallbacks for old browsers which do not support it natively.

 * :py:class:`snorky.request_handlers.http.BackendHTTPHandler`: This is a more limited request handler. It works over plain HTTP and each connection can only exchange one message from each party, one for the request, and one for the response. It's usually used in order to :doc:`expose a backend interface<backend>`.

Application
~~~~~~~~~~~

In Tornado, a :py:class:`tornado.web.Application` is *a collection of request handlers that make up a web application*.

This class manages a set of routes, each one consisting of an URL pattern, a request handler class and optionally a set of parameters which are fed to the :py:class:`tornado.web.RequestHandler` ``__init__`` function. :py:func:`SnorkyWebSocketHandler.get_route` returns such a route for a WebSocket request handler.

:py:func:`tornado.web.Application.listen` sets up an HTTP server listening on the specified port and address. If no address is specified, it will listen in all interfaces, both in IPv4 and IPv6, if supported.

Conclusion
~~~~~~~~~~

.. only:: not latex

    The following UML diagram resumes the collaborations explained above.

.. only:: latex

    The UML diagram in :num:`overview-uml` resumes the collaborations explained above.

The next chapters will cover further details on the inner working of each of the components and how they can be extended.

.. _overview-uml:

.. figure:: /_images/overview.*
    :align: center

    The overview of Snorky core classes as a simplistic UML diagram.
