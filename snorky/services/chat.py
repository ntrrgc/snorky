from snorky.services.base import RPCService, RPCError, rpc_command
from snorky.types import MultiDict
from datetime import datetime


class ChatService(RPCService):
    def __init__(self, name):
        super(ChatService, self).__init__(name)

        # channel : str -> set<Client>
        self.subscriptions = MultiDict()
        # Client -> set<channel : str>
        self.subscriptions_by_client = MultiDict()

    def get_time(self):
        from dateutil.tz import tzlocal
        return datetime.now(tz=tzlocal()).isoformat()

    @rpc_command
    def join(self, req, channel):
        if self.subscriptions.in_set(channel, req.client):
            raise RPCError("Already joined")

        # Send presence to other members
        self.send_presence(channel, req.client, "joined")

        self.subscriptions.add(channel, req.client)
        self.subscriptions_by_client.add(req.client, channel)

        return {
            "members": [client.identity for client
                        in self.subscriptions.get_set(channel)]
        }

    @rpc_command
    def leave(self, req, channel):
        try:
            self.subscriptions.remove(channel, req.client)
            self.subscriptions_by_client.remove(req.client, channel)

            # Send presence to remaining users
            self.send_presence(channel, req.client, "left")
        except KeyError:
            raise RPCError("Not joined")

    @rpc_command
    def send(self, req, channel, body):
        if not self.subscriptions.in_set(channel, req.client):
            raise RPCError("Not joined")

        message = {
            "type": "message",
            "from": req.client.identity,
            "channel": channel,
            "body": body,
            "timestamp": self.get_time(),
        }

        for client in self.subscriptions.get_set(channel):
            self.send_message_to(client, message)

    def send_presence(self, channel, client, status):
        presence = {
            "type": "presence",
            "from": client.identity,
            "channel": channel,
            "status": status,
            "timestamp": self.get_time(),
        }
        for client in self.subscriptions.get_set(channel):
            self.send_message_to(client, presence)

    def client_disconnected(self, client):
        for channel in self.subscriptions_by_client.get_set(client):
            self.subscriptions.remove(channel, client)
            # Send presence to remaining users
            self.send_presence(channel, client, "left")

        self.subscriptions_by_client.clear_set(client)
