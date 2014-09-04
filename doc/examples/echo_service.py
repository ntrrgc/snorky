from snorky.services.base import Service

class EchoService(Service):
    def process_message_from(self, client, msg):
        self.send_message_to(client, msg)
