# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
try:
    from inspect import signature
except ImportError:
    from funcsigs import signature
from snorky.log import snorky_log
from snorky.types import with_metaclass


class Service(object):
    """Subclass this class and redefine ``process_message_from()`` in order to
    create a new service.
    """
    def __init__(self, name):
        self.name = name

    def process_message_from(self, client, msg):
        """Called when a message is received.

        ``msg`` contains the message as a JSON decoded entity. msg and all
        their descedants are always hashable.
        """
        raise NotImplemented

    def send_message_to(self, client, msg):
        """Sends a message to a client through the current service.

        Services should use this method instead of calling directly to
        ``client.send()`` in order to add the service header.
        """
        client.send({
            "service": self.name,
            "message": msg,
        })

    def client_connected(self, client):
        """Called each time a client connects to Snorky through a channel which
        is connected to the same :py:class:`snorky.ServiceRegistry` than this
        service.

        Exceptionally, this method is not called when a client connects from a
        short-lived channel like
        :py:class:`snorky.request_handlers.http.BackendHTTPHandler`.
        """
        pass

    def client_disconnected(self, client):
        """Called each time a client disconnects from Snorky through a channel
        which is connected to the same :py:class:`snorky.ServiceRegistry` than
        this service.

        Exceptionally, this method is not called when a client connects from a
        short-lived channel like
        :py:class:`snorky.request_handlers.http.BackendHTTPHandler`.
        """
        pass


class InvalidMessage(Exception):
    pass


class RPCError(Exception):
    """An error response is sent to the client when this exception is thrown.
    """
    pass

def ellipsis(string, max_length=100):
    """Returns a length limited version of a string, up to ``max_length``
    characters.

    If the string is longer it will be cut preserving the starting part and an
    ellipsis will be added.
    """
    if len(string) <= max_length:
        return string
    else:
        return string[:max_length - 3] + "..."

def format_call(command, params):
    """Returns a short textual representation of a call."""
    return ellipsis("%s(%s)" % (
        command,
        json.dumps(params, sort_keys=True, ensure_ascii=False,
                            separators=(', ', ': '))
    ))

class Request(object):
    """Represents a request against an RPC service and provides methods to
    resolve it.
    """
    __slots__ = ("service", "client", "command", "call_id", "params",
                 "resolved", "debug")

    def __init__(self, service, client, msg):
        self.service = service
        """The service instance this request was sent against."""
        self.client = client
        """The client which initiated this requests."""
        self.resolved = False
        """Whether the request has been resolved either with success or
        failure."""
        self.debug = False
        try:
            self.call_id = msg.get("callId", None)
            """An integer the client may set in order to associate each
            response with the request that caused it."""
            self.command = msg["command"]
            """The requested command."""
            self.params = msg["params"]
            """The specified parameters as a dictionary."""
        except (KeyError, TypeError):
            raise InvalidMessage

    def reply(self, data):
        """Sends a successful response.

        Each request can be resolved one time. Calling this method twice or
        calling both ``reply()`` and ``error()`` will trigger a server error.
        """
        if self.resolved:
            raise RuntimeError("This request has already been resolved")

        data = {
            "type": "response",
            "callId": self.call_id,
            "data": data
        }
        if data["callId"] is None:
            del data["callId"]
        self.service.send_message_to(self.client, data)

        self.resolved = True

    def error(self, msg):
        """Sends an error response.

        Each request can be resolved one time. Calling this method twice or
        calling both ``reply()`` and ``error()`` will trigger a server error.
        """
        if self.resolved:
            raise RuntimeError("This request has already been resolved")

        self.service.send_message_to(self.client, {
            "type": "error",
            "callId": self.call_id,
            "message": msg
        })
        self.resolved = True

    def format_call(self):
        """Returns a short textual representation of the call."""
        return format_call(self.command, self.params)


def rpc_command(method):
    """Decorator to declare an RPC command."""
    method.is_rpc_command = True
    return method


def rpc_asynchronous(method):
    """Decorator to declare an asynchronous RPC command.

    :func:`rpc_command` must also be used for this to make effect. The order in
    which both decorators are applied is not important."""
    method.is_asynchronous = True
    return method


class RPCMeta(type):
    """Metaclass used to populate the ``rpc_commands`` set in :class:RPCService
    subclasses."""
    def __new__(cls, name, bases, attrs):
        new_class = super(RPCMeta, cls).__new__(cls, name, bases, attrs)

        # Create a new set based on the allowed commands of the superclass.
        new_rpc_commands = set(new_class.rpc_commands)

        # Add each method decorated with @rpc_command
        for name, value in attrs.items():
            if getattr(value, "is_rpc_command", False):
                new_rpc_commands.add(name)

        # Froze the set and put it in the new class
        new_class.rpc_commands = frozenset(new_rpc_commands)

        return new_class


class RPCService(with_metaclass(RPCMeta, Service)):
    """Subclass this class to make RPC services.

    RPC services expose a more convenient interface than bare Snorky services.
    """
    rpc_commands = frozenset()

    def process_message_from(self, client, msg):
        """Processes an incoming message, which should be an RPC request."""
        try:
            request = Request(self, client, msg)
        except InvalidMessage:
            snorky_log.warning('Invalid format in RPC service "%s". Message: %s'
                            % (self.name, msg))
            # Discard silently
            return

        return self.process_request(request)

    def process_request(self, request):
        """Attends the request from the client, checking the requested command
        exists and the signature is correct. If the request is well formed, the
        command specified by the request is executed.

        Exceptions are catched, triggering error responses being sent to the
        client.
        """
        if request.command not in self.rpc_commands:
            request.error("Unknown command")
            return

        method = getattr(self, request.command)
        try:
            # Check signature
            signature(method).bind(request, **request.params)
        except TypeError:
            snorky_log.warning('Invalid params in RPC service "%s": %s'
                            % (self.name, request.format_call()))
            request.error("Invalid params")
            return

        # Signature is correct, call the method
        try:
            reply_data = method(request, **request.params)
            # If the method returns something, use that as a reply message
            if reply_data is not None:
                request.reply(reply_data)
            elif not getattr(method, "is_asynchronous", False) and \
                    not request.resolved:
                # If the method is not marked as asynchronous and it returned
                # None, reply with None.
                request.reply(None)
        except RPCError as ex:
            error_name = ex.args[0] if len(ex.args) > 0 else "Exception"
            snorky_log.info("%s in RPC service \"%s\", call: %s %s"
                         % (error_name, self.name, request.command,
                            request.params))
            request.error(error_name)
        except:
            if request.debug:
                # In unit tests, let this exception propagate
                raise
            snorky_log.exception('Unhandled exception in RPC service "%s": %s'
                              % (self.name, request.format_call()))
            request.error("Internal error")
