Connecting to services
======================

More often than not, you will want to connect to Snorky from Javascript in a web application. For this purpose, there is an official connector, **Snorky.js**.

Dependencies
~~~~~~~~~~~~

Snorky.js has a few dependencies that must be included before it:

 * `my.class.js <https://github.com/jiem/my-class>`_: A lightweight class library for Javascript. Javascript does not have a declarative syntax to define classes, which makes writing them a tedious and error-prone process. This is one of many libraries trying to fill that gap.

   Once initialized, this class factory is stored in :js:class:`Snorky.Class`.

 * `js-signals <http://millermedeiros.github.io/js-signals/>`_: An event library for Javascript. All events defined in Snorky are created with this, which allows you to easily add and remove any number of handlers for each event.

   Once initialized, the event class is stored in :js:class:`Snorky.Signal`. Although in vanilla usage this class will be the same as js-signal's :js:class:`signals.Signal`, additional initialization code may replace it with a subclass which provides additional functionality.

   For example, Angular-Snorky does this in order to request a ``$digest`` cycle to AngularJS every time an event is dispatched in order to update the view.

Promises
--------

Additionally, Snorky returns promises for service requests. In order for this to work, Snorky needs a ``Promise`` class.

By default it will use `the Promise class defined in ECMAScript 6 <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise>`_, but it can be changed to any other class with a similar interface running the following code after ``snorky.js`` has been included:

.. code:: javascript

    Snorky.Promise = <your promise class>;

Particularly, Angular-Snorky does this as part of its initialization in order to make Snorky work with `Angular promises <https://docs.angularjs.org/api/ng/service/$q>`_ instead of ES6 promises.

If you choose to use ES6 promises, chances are you will need a polyfill since, at the time of writing, most browsers don't support them out of the box yet. `Jake Archibald <https://github.com/jakearchibald>`_ has published `such polyfill at GitHub <https://github.com/jakearchibald/es6-promise>`_.

Socket class
------------

Snorky needs a socket class in order to connect to the server. This class must have the `WebSocket interface <http://www.w3.org/TR/2011/WD-websockets-20110419/>`_.

Nowadays most browsers in use support WebSocket natively, making it an excellent choice for a number of applications. In cases where older browser support is needed (e.g. IE9 or older) `SockJS <https://github.com/sockjs/sockjs-client>`_ provides a viable alternative, providing fallback transports for old browsers but using WebSocket under the hood in modern browsers.

Connecting
~~~~~~~~~~

Once ``snorky.js`` and all the dependencies needed have been included, the ``Snorky`` class will be available in the global namespace.

.. js:class:: Snorky(socketClass, address, services[, options])

    Manages a connection to Snorky and its associated service connectors. Connection is automatically made on object creation.

    :param class socketClass: The socket class which will be used for the connection.

        It must provide the same interface as :js:class:`WebSocket`. It's usually either ``WebSocket`` or ``SockJS``.

        Note that this parameter requests the class itself, not an instance.

    :param String address: The URL which will be passed to the constructor of ``socketClass``. Note that WebSocket uses ``ws://`` or ``wss://`` as protocol while ``SockJS`` uses ``http://`` or ``https://`` instead.

    :param Object services: A dictionary matching each service name with a class. Those classes will be used to interact with the services from Javascript.

    :param Object options: An optional dictionary with additional options. At the moment only one option is supported:

        .. js:attribute:: debug

            Whether to print debugging information to the console when the connection is made or lost.


    .. js:attribute:: address

        The address to which the socket has been connected.

    .. js:attribute:: socketClass

        The socket class used.

    .. js:attribute:: debug

        Whether the debug mode is enabled.

    .. js:attribute:: services

        Dictionary of **service instances** available, indexed by name.

    .. js:attribute:: isConnected

        Whether there is an active connection to the server.

    .. js:attribute:: isConnecting

        Whether a connection to the server is being attempted.

    .. js:function:: logDebug(format[, ...])

        Logs text in the console, but only if the debug mode is active.

        Accepts either any object or a format string with arguments like :js:func:`console.debug`.

    **Events**

    .. js:attribute:: connected

        Event raised when a connection is successfully made to the server.

    .. js:attribute:: disconnected

        Event raised when a connection is closed, either voluntarily or due to a network failure.

Service connectors
~~~~~~~~~~~~~~~~~~

Snorky.js has a number of classes which provide an interface to the Snorky services from the client side. They should inherit from :js:class:`Snorky.Service`, or, more frequently, from :js:class:`Snorky.RPCService`.

.. js:class:: Snorky.Service(name, snorky)

    Provides an interface to a Snorky service.

    Usually you don't need to create instances of this class directly, :js:class:`Snorky` does automatically.

    :param String name: The name of the service instance in the server side.

    :param Snorky snorky: The Snorky object this service connector belongs.

    .. js:attribute:: name

        The service name.

    .. js:attribute:: snorky

        The Snorky object this service connector belongs.

    .. js:function:: init

        Initialization hook. You usually extend it in your subclasses in order to listen for events, register attributes or do other initialization work.

    .. js:function:: sendMessage(message)

        Sends a message to the service. ``message`` must be serializable to JSON.

    **Events**

    .. js:attribute:: packetReceived

        Event raised when a new message arrives to this service.

.. js:class:: Snorky.RPCService(name, snorky)

    Provides a convenient connector for RPC services.

    If you are writing a connector to an RPC service you should subclass this class instead of :js:class:`Snorky.Service`.

    .. js:function:: rpcCall(command, params)

        :param String command: The command to request
        :param Object params: A **dictionary** of parameters.

        :returns: An `A+ Promise <http://promisesaplus.com/>`_.

            If the remote call is successful, the promise will be fulfilled with the value returned from the remote call.

            If the remote call fails, the promise will be rejected with the error message sent by Snorky.

        Makes an RPC call.

    .. js:function:: addRPCMethods(methods)

        :param Array methods: A list of command names

        This is an static method.

        Adds the specified RPC commands as methods to the class. For each command a method with the same name will be generated which will accept one argument with the RPC parameters and will return a Promise.

        Internally these methods will call to :js:func:`Snorky.RPCService.addRPCMethods`.

    **Events**

    .. js:attribute:: notificationReceived

        Event raised when a notification is received; that is, a message whose ``type`` is neither ``response`` or ``error``.

SimplePubSub connector
~~~~~~~~~~~~~~~~~~~~~~

The following service connector makes easy to use the ``SimplePubSubService`` example service described in :ref:`example-pubsub`:

.. literalinclude:: /examples/simple_pubsub.js
    :language: javascript

Connection example
~~~~~~~~~~~~~~~~~~

The following example connects to an Snorky server with the ``SimplePubSub`` service described above.

.. code-block:: javascript

    var snorky = new Snorky(WebSocket, "ws://localhost:8001/ws", {
        "pubsub": SimplePubSub
    });

``snorky.services`` contains the instantiated services. The following code would request a subscription.

.. code-block:: javascript

    snorky.services.pubsub.subscribe({ /* no parameters */ })
      .then(function (returnValue) {
        console.log("Subscribed!");
      });

.. note::

    The services can be used even before the connection has been established. Snorky will store the messages in a buffer and send them when the connection is made.

Event handlers can be added too at this stage. The following would log messages published.

.. code-block:: javascript

    snorky.services.pubsub.publicationReceived.add(
      function(publishedText) {
        console.log(publishedText)
      });

Conclusion
~~~~~~~~~~

This chapter has shown the basics of the Javascript Snorky connector, including how to include it, how connect to it and how services connector can be written and used.

The following chapter will cover the backend interface.
