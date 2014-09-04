from abc import abstractproperty, abstractmethod

class Client(object):
    """Represents a connection to the WebSocket server.

    This is an abstract base class not associated to any protocol.
    """

    def __init__(self):
        self.identity = None

    @abstractproperty
    def remote_address(self):
        """An address to the remote client, usually an IP address."""
        pass

    @abstractmethod
    def send(self, msg):
        """Send a message to the client. The message must be a JSON entity,
        e.g. dictionary, string or number.
        """
        pass
