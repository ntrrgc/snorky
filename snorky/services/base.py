import json
try:
    from inspect import signature
except ImportError:
    from funcsigs import signature
from tornado.log import gen_log
from snorky.types import with_metaclass


class Service(object):
    def __init__(self, name):
        self.name = name

    def process_message_from(self, client, msg):
        raise NotImplemented

    def send_message_to(self, client, msg):
        client.send({
            "service": self.name,
            "message": msg,
        })

    def client_connected(self, client):
        pass

    def client_disconnected(self, client):
        pass


class InvalidMessage(Exception):
    pass


class RPCError(Exception):
    pass

def ellipsis(string, max_length=100):
    if len(string) <= max_length:
        return string
    else:
        return string[:max_length - 3] + "..."

def format_call(command, params):
    return ellipsis("%s(%s)" % (
        command,
        json.dumps(params, sort_keys=True, ensure_ascii=False,
                            separators=(', ', ': '))
    ))

class Request(object):
    __slots__ = ("service", "client", "command", "call_id", "params",
                 "resolved", "debug")

    def __init__(self, service, client, msg):
        self.service = service
        self.client = client
        self.resolved = False
        self.debug = False
        try:
            self.call_id = msg["callId"]
            self.command = msg["command"]
            self.params = msg["params"]
        except (KeyError, TypeError):
            raise InvalidMessage

    def reply(self, data):
        if self.resolved:
            raise RuntimeError("This request has already been resolved")

        self.service.send_message_to(self.client, {
            "type": "response",
            "callId": self.call_id,
            "data": data
        })
        self.resolved = True

    def error(self, msg):
        if self.resolved:
            raise RuntimeError("This request has already been resolved")

        self.service.send_message_to(self.client, {
            "type": "error",
            "callId": self.call_id,
            "message": msg
        })
        self.resolved = True

    def format_call(self):
        return format_call(self.command, self.params)


def rpc_command(method):
    method.is_rpc_command = True
    return method


def asynchronous(method):
    method.is_asynchronous = True
    return method


class RPCMeta(type):
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
    rpc_commands = frozenset()

    def process_message_from(self, client, msg):
        try:
            request = Request(self, client, msg)
        except InvalidMessage:
            gen_log.warning('Invalid format in RPC service "%s". Message: %s'
                            % (self.name, msg))
            # Discard silently
            return

        return self.process_request(request)

    def process_request(self, request):
        if request.command not in self.rpc_commands:
            request.error("Unknown command")
            return

        method = getattr(self, request.command)
        try:
            # Check signature
            signature(method).bind(request, **request.params)
        except TypeError:
            gen_log.warning('Invalid params in RPC service "%s": %s'
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
                # If the method is not marked as asynchronous, it returned
                # None and the request is not marked as asynchronous, then
                # reply with None.
                request.reply(None)
        except RPCError as ex:
            error_name = ex.args[0] if len(ex.args) > 0 else "Exception"
            gen_log.info("%s in RPC service \"%s\""
                         % (error_name, self.name))
            request.error(error_name)
        except:
            if request.debug:
                # In unit tests, let this exception propagate
                raise
            gen_log.exception('Unhandled exception in RPC service "%s": %s'
                              % (self.name, request.format_call()))
            request.error("Internal error")
