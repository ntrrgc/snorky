# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.log import snorky_log
from snorky.hashable import make_hashable
import json


class ServiceRegistry(object):
    """Manages a set of services identified by name and delivers messages to
    them.
    """

    def __init__(self, services=None):
        self.registered_services = {}
        if services:
            for service in services:
                self.register_service(service)

    def register_service(self, service):
        """Adds a new service to this registry."""
        self.registered_services[service.name] = service

    def unregister_service(self, service):
        """Removes a service from this registry."""
        del self.registered_services[service.name]

    def process_message_from(self, client, msg):
        """Delivers a message to the destination service specified in it, which
        should be associated with this registry.
        """
        try:
            service_name = msg["service"]
            content = msg["message"]
        except KeyError:
            snorky_log.warning("Malformed message from client %s: %s"
                           % (client.remote_address, msg))
            return

        try:
            service = self.registered_services[service_name]
        except KeyError:
            snorky_log.warning(
                'Message for non existing service "%s" from client %s'
                % (service_name, client.remote_address))
            return

        service.process_message_from(client, content)

    def process_message_raw(self, client, msg):
        """Decodes a message encoded as a JSON character string and sends it to
        the destination service."""
        try:
            decoded_msg = make_hashable(json.loads(msg))
        except ValueError:
            snorky_log.warning('Invalid JSON from client %s: %s'
                            % (client.remote_address, msg))
            return

        return self.process_message_from(client, decoded_msg)

    def client_connected(self, client):
        """This method must be called every time a new client connects to the
        server through a request handler associated with this registry.
        """
        for service in self.registered_services.values():
            service.client_connected(client)

    def client_disconnected(self, client):
        """This method must be called every time a client disconnects from the
        server.
        """
        for service in self.registered_services.values():
            service.client_disconnected(client)
