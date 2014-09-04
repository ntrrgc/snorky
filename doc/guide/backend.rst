Wiring a backend
================

Sometimes there are some actions in your system that you only want to allow to certain parties, like trusted servers in your network. In Snorky, those are called *the backend*.

Special services are often exposed to the backend servers, which allow controlling restricted aspects of other services. This is possible due to Snorky allowing to have several service registries.

Pub Sub with backend
~~~~~~~~~~~~~~~~~~~~

Sometimes you want a Pub Sub service when the end clients are not allowed to publish, just to subscribe, and publications can only be made by a trusted computer.

Snorky comes with a Pub Sub service, :py:class:`snorky.services.pubsub.PubSubService` which already implements this with another backend service :py:class:`snorky.services.pubsub.PubSubBackend`.

Both could be used like this:

.. literalinclude:: /examples/pubsub_backend.py

Note the backend and the frontend interface are exposed in **different ports**. This is not a requirement, but makes firewalling easier. For example, the backend port may only be exposed to the local network while the frontend port will usually be exposed to the entire world.

The API key
~~~~~~~~~~~

In order to provide additional security, the ``BackendHTTPHandler`` requires a API key or password in order to interact with its associated services. This key will be sent as an HTTP header with name ``X-Backend-Key``.

Make sure to choose an API key and make it secret.

Even if you make the backend interface available only to computers in a restricted network or only to the same machine that runs Snorky, the API key still provides a security benefit, avoiding successful attacks to other server processes to escalate into Snorky.

Exposing the backend interface only to the local machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you only need to communicate with the backend interface within the same machine Snorky runs, you can bind ``backend_application`` to the local address, thus avoiding it to be reachable from the outside.

In order to do this, replace the ``listen`` call for ``backend_application`` in the code above with this:

.. code:: python

    backend_application.listen(5801, address="127.0.0.1")

Communicating with the backend interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A JSON HTTP request is enough to send a command to the Snorky backend interface. Virtually every programming language has support for this kind of communication.

The request must contain in the body the JSON message including the service header, encoded in UTF-8.

The following code shows an example which sends a ``publish`` command in Python using `requests <http://docs.python-requests.org/>`_.

.. literalinclude:: /examples/talk_backend.py

The body of the response will also have a JSON object encoded in UTF-8. It will consist on the service response wrapped in the service header.

The following code would print the returned value from the service or signal a failure:

.. literalinclude:: /examples/talk_backend_response.py

.. note::

    The Snorky HTTP transport is not aware of the RPC system so service failures will still send responses with the ``200 OK`` code, yet they will appoint the error message in the body of the RPC response.

Note that in this case the call returns nothing, so the command response would be ``None`` (equivalent to JSON ``null``).

Using the backend connector
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sending the requests with HTTP libraries is prone to code repetition, so it's advised to write helper functions or classes that take care of the low level communication.

If the application that you are connecting to Snorky is written in Python, you can use the Snorky backend connector for this purpose. For example, the code before would be reduced to this:

.. literalinclude:: /examples/talk_backend_connector.py

The Snorky backend connector will automatically serialize the request into JSON, send it to the HTTP endpoint, receive the response, deserialize it, remove the service header and return the RPC call return value.

If the service returns with error, a ``SnorkyError``, specifying the error message as an argument. If there is another kind of error, e.g. the Snorky server is not available, a ``RuntimeError`` is thrown, with more details in the error argument also.
