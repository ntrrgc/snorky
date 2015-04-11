# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.services.base import RPCService, RPCError, rpc_command


class MessagingService(RPCService):
    def __init__(self, name):
        super(MessagingService, self).__init__(name)
        self.participants = {}        # participant name -> client
        self.client_participants = {} # client -> set(participant names)

    @rpc_command
    def registerParticipant(self, req, name):
        """RPC method.

        Assign the client a name for use in the messaging service.
        """
        if name in self.participants:
            raise RPCError("Name already registered")

        if not self.is_name_allowed(req.client, name):
            raise RPCError("Name not allowed")

        self.participants[name] = req.client
        self.client_participants.setdefault(req.client, set()).add(name)

    @rpc_command
    def unregisterParticipant(self, req, name):
        """RPC method.

        Free a name previously registered by the client.
        """
        try:
            if self.participants[name] != req.client:
                # Don't let clients unregister other participants
                raise RPCError("Invalid participant")

            del self.participants[name]
            self.client_participants[req.client].remove(name)
            if len(self.client_participants[req.client]) == 0:
                del self.client_participants[req.client]
        except KeyError:
            raise RPCError("Unknown participant")

    @rpc_command
    def listParticipants(self, req):
        """RPC method.

        Returns a list containing the names of the currently available users.
        """
        return sorted(self.participants.keys())

    @rpc_command
    def send(self, req, sender, dest, body):
        try:
            if self.participants[sender] != req.client:
                # The user tries to send a message impersonating other user,
                # deny.
                raise RPCError("Invalid sender")
        except KeyError:
            # The sender name is not a know participant
            raise RPCError("Invalid sender")

        try:
            dest_client = self.participants[dest]
        except KeyError:
            raise RPCError("Unknown destination")

        self.send_message_to(dest_client, {
            "type": "message",
            "sender": sender,
            "dest": dest,
            "body": body
        })

    def is_name_allowed(self, client, name):
        """Substitute this method in order to disallow names not
        matching a set of rules you define.

        It must return ``True`` if the specified name is acceptable for the
        requester client.

        By default it allows every name to all users.
        """
        # Default policy: allow all names
        return True

    def client_disconnected(self, client):
        if client in self.client_participants:
            for participant_name in self.client_participants[client]:
                del self.participants[participant_name]
            del self.client_participants[client]
