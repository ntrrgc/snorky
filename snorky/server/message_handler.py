from tornado.log import gen_log


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

    def client_connected(self, client):
        pass

    def client_disconnected(self, client):
        pass
