# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.services.base import RPCService, RPCError, rpc_command
from snorky.types import MultiDict
from datetime import datetime


class ChatService(RPCService):
    def __init__(self, name):
        super(ChatService, self).__init__(name)

        # (channel) : obj -> set<Client>
        self.clients_by_channel = MultiDict()
        # (Client) -> set<channel : obj>
        self.channels_by_client = MultiDict()
        # (identity : obj, channel : obj) -> set<Client>
        self.clients_by_identity_and_channel = MultiDict()
        # (channel : obj) -> set<Identity>
        self.identities_by_channel = MultiDict()

    def get_time(self):
        from dateutil.tz import tzlocal
        return datetime.now(tz=tzlocal()).isoformat()

    def check_identity(self, client):
        if client.identity is None:
            raise RPCError("Not authenticated")

    @rpc_command
    def join(self, req, channel):
        client = req.client
        identity = client.identity

        self.check_identity(client)

        if self.clients_by_channel.in_set(channel, client):
            raise RPCError("Already joined")

        if identity not in self.identities_by_channel.get_set(channel):
            # Send presence to other members
            self.send_presence(channel, client, "joined")
            self.identities_by_channel.add(channel, identity)

        self.clients_by_channel.add(channel, client)
        self.channels_by_client.add(client, channel)
        self.clients_by_identity_and_channel.add(
            (identity, channel), req.client)

        return {
            "members": list(self.identities_by_channel.get_set(channel))
        }

    @rpc_command
    def leave(self, req, channel):
        client = req.client

        if not self.clients_by_channel.in_set(channel, client):
            raise RPCError("Not joined")

        self.do_leave(client, channel)

    def do_leave(self, client, channel):
        identity = client.identity

        self.clients_by_channel.remove(channel, client)
        self.channels_by_client.remove(client, channel)
        self.clients_by_identity_and_channel.remove(
            (identity, channel), client)

        if len(self.clients_by_identity_and_channel.get_set(
            (identity, channel))) == 0:
            # User is not connected from elsewhere
            self.identities_by_channel.remove(channel, identity)
            # Send presence to remaining users
            self.send_presence(channel, client, "left")

    @rpc_command
    def send(self, req, channel, body):
        if not self.clients_by_channel.in_set(channel, req.client):
            raise RPCError("Not joined")

        message = {
            "type": "message",
            "from": req.client.identity,
            "channel": channel,
            "body": body,
            "timestamp": self.get_time(),
        }

        for client in self.clients_by_channel.get_set(channel):
            self.send_message_to(client, message)

    def send_presence(self, channel, client, status):
        presence = {
            "type": "presence",
            "from": client.identity,
            "channel": channel,
            "status": status,
            "timestamp": self.get_time(),
        }
        for client in self.clients_by_channel.get_set(channel):
            self.send_message_to(client, presence)

    @rpc_command
    def read(self, req, channel):
        notification = {
            "type": "read",
            "channel": channel,
            "timestamp": self.get_time(),
        }

        for client in self.clients_by_identity_and_channel.get_set(
                            (req.client.identity, channel)):
            if client is not req.client:
                self.send_message_to(client, notification)


    def client_disconnected(self, client):
        channels = list(self.channels_by_client.get_set(client))
        for channel in channels:
            self.do_leave(client, channel)
