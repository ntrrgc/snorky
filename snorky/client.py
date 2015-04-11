# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
