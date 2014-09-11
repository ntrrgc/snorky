Writing services
================

.. automodule:: snorky.services.base

    Services are the main construction blocks of Snorky. In this section you will learn how services work and how they are created.

    The Snorky service protocol
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Every message send through Snorky must be directed to a service, identified by a service *name*, which shall be an string.

    The message itself must be a JSON entity. That includes strings, numbers, arrays, objects and the ``null`` value. The `JSON web site <http://json.org/>`_ contains the full specification of the language, describing each data type in detail.

    Often in this documentation, JSON arrays will be referred as **lists** and JSON objects will be referred as **dictionaries**, matching the Python data types those primitive types are transformed into.

    The following is an example of a message sent to an ``echo`` service, as it could be sent through WebSocket:

    .. code-block:: javascript

        {"service":"echo","message":"Hello"}

    The Service definition
    ~~~~~~~~~~~~~~~~~~~~~~

    A service class must inherit from :py:class:`Service` or one of their descendants. It must provide an implementation for the method :py:func:`Service.process_message_from`.

    The following example service sends back to the client each message it receives:

    .. literalinclude:: /examples/echo_service.py

    .. autoclass:: Service

        .. automethod:: Service.process_message_from
        .. automethod:: Service.send_message_to
        .. automethod:: Service.client_connected
        .. automethod:: Service.client_disconnected


    RPC services
    ~~~~~~~~~~~~

    Although you could write services inheriting directly from :py:class:`Service` and using its simple methods, they often fall short.

    Most services often work, at least partially, in a request-response fashion, ocasionally sending notifications to the client that are not part of the response.

    Snorky leverages this pattern through the subclass :py:class:`RPCService`. Currently, all instanciable Snorky services are RPC services, and chances are yours will be too.

    .. autoclass:: RPCService

    Commands
    --------

    Each RPC service has a series of *commands* which are defined as methods with the :py:func:`rpc_command` decorator.

    Commands accept a set of parameters which is specified in the signature of the method. They may have default values.

    The return value of a command is sent automatically to the requester client. Every entity that can be serialized as JSON is a valid return value.

    If the method does not return anything, ``null`` is sent as response. This is usually done in order to signal that the request has been processed successfully but there is nothing interesting to send in return.

    The following service calculates sums and logarithms in response to client requests:

    .. literalinclude:: /examples/simple_rpc.py

    .. note::

        The names of RPC commands and their parameters are usually written in ``camelCase`` instead of ``snake_case`` because they are exposed in Javascript with the same name.

    Exceptions
    ----------

    Sometimes you want to signal an error condition. In this cases, instead of returning, raise an instance of :py:class:`RPCError`. For example, ``raise RPCError("Not authorized")``.

    Snorky already signals some error conditions by default:

    * If a client requests a non existing command, ``Unknown command`` is raised.

    * If the request params don't fit the ones specified in the method, i.e. nonexistent parameters are used or required parameters are ommited, ``Invalid params`` is raised.

    * If an exception different from :py:class:`RPCError` is raised while the command is being handled, ``Internal error`` is raised.

    Asynchronous commands
    ---------------------

    Sometimes the processing of a command has to be temporarily suspended until a certain event occurs.

    For example, the command may need to perform a HTTP request. It's undesirable for the command to block the entire server, as that would kill performance. Instead, asynchronous requests shall be used.

    Such RPC commands must use the decorator :py:func:`rpc_asynchronous`, in addition to :py:func:`rpc_command`.

    Asynchronous RPC commands do not send a response when the method call returns nothing. Instead, is expected that the request will be replied eventually as a response to another event.

    The ``req`` parameter in RPC commands contains a :py:class:`Request` object with methods to send either a successful reply or signal an error to the client.

    The Request class
    ~~~~~~~~~~~~~~~~~

    .. autoclass:: Request

        .. automethod:: Request.reply
        .. automethod:: Request.error

        .. autoattribute:: Request.client

            The requester client. It complies with the interface defined in :py:class:`snorky.client.Client`.

        .. autoattribute:: Request.command

            The requested command name.

        .. autoattribute:: Request.params

            The params supplied by the client, as a dictionary.

        .. autoattribute:: Request.resolved

            ``True`` if the request has been resolved either with a successful reply or with an error.

    .. _example-pubsub:

    Sending notifications
    ~~~~~~~~~~~~~~~~~~~~~

    At any moment you can send an arbitrary message to any client of your service. These messages should be JSON objects and should contain a ``type`` attribute which must be neither ``response`` or ``error``, since these types are used by RPC calls.

    Messages which are neither of type ``response`` or ``error`` are called *notifications*.

    The following example shows a simple PubSub service in which any client can publish a message to every client subscripted (including itself):

    .. literalinclude:: /examples/simple_pubsub.py

    Conclusion
    ~~~~~~~~~~

    This chapter has explained how to built services with Snorky.

    Although Snorky comes with a few services, often you will need to extend them or create small specific services for your application. Nevertheless, Snorky utilities should not make this task difficult.

    The next chapter will explain how to connect to Snorky from a web application and how service connectors are created in Javascript.
