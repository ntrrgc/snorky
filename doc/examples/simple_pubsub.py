from snorky.services.base import RPCService, rpc_command

class MinimalPubSubService(RPCService):
    def __init__(self, name):
        # Call parent constructor
        RPCService.__init__(self, name)

        self.clients = set()

    @rpc_command
    def subscribe(self, req):
        if req.client not in self.clients:
            self.clients.add(req.client)

    @rpc_command
    def unsubscribe(self, req):
        if req.client in self.clients:
            self.clients.remove(req.client)

    def client_disconnected(self, client):
        # Never forget to remove the client from the set after disconnection!
        if client in self.clients:
            self.clients.remove(client)

    @rpc_command
    def publish(self, req, message):
        for client in self.clients:
            self.send_message_to(client, {
                "type": "publication",
                "message": message,
            })
