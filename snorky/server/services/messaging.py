from snorky.server.services.base import RPCService, RPCError, rpc_command


class MessagingService(RPCService):
    def __init__(self, name):
        super(MessagingService, self).__init__(name)
        self.participants = {}

    @rpc_command
    def register_participant(self, req, name):
        if name in self.participants:
            raise RPCError("Name already registered")

        if not self.is_name_allowed(req.client, name):
            raise RPCError("Name not allowed")

        self.participants[name] = req.client
        return "OK"

    @rpc_command
    def unregister_participant(self, req, name):
        try:
            del self.participants[name]
            return "OK"
        except KeyError:
            raise RPCError("Unknown participant")

    @rpc_command
    def list_participants(self, req):
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
            "body": body
        })
        return "OK"

    def is_name_allowed(self, client, name):
        # Default policy: allow all names
        return True

