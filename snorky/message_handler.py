from tornado.log import gen_log
import json


class MessageHandler(object):
    def __init__(self, services=None):
        self.registered_services = services or {}

    def register_service(self, service):
        self.registered_services[service.name] = service

    def unregister_service(self, service):
        del self.registered_services[service.name]

    def process_message_from(self, client, msg):
        try:
            service_name = msg["service"]
            content = msg["message"]
        except KeyError:
            gen_log.warning("Malformed message from client %s: %s"
                           % (client.remote_address, msg))
            return

        try:
            service = self.registered_services[service_name]
        except KeyError:
            gen_log.warning(
                'Message for non existing service "%s" from client %s'
                % (service_name, client.remote_address))
            return

        service.process_message_from(client, content)

    def process_message_raw(self, client, msg):
        try:
            decoded_msg = json.loads(msg)
        except ValueError:
            gen_log.warning('Invalid JSON from client %s: %s'
                            % (client.remote_address, msg))
            return

        return self.process_message_from(client, decoded_msg)

    def client_connected(self, client):
        for service in self.registered_services.values():
            service.client_connected(client)

    def client_disconnected(self, client):
        for service in self.registered_services.values():
            service.client_disconnected(client)
