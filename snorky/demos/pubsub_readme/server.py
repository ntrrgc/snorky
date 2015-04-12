import os
from tornado.ioloop import IOLoop
from tornado.web import Application
from snorky import ServiceRegistry

from snorky.request_handlers.websocket import SnorkyWebSocketHandler
from snorky.services.pubsub import PubSubService

if __name__ == "__main__":
    service_registry = ServiceRegistry()
    # Every service instance has a name, here: pubsub
    service_registry.register_service(PubSubService("pubsub"))

    # Register HTTP endpoint: ws://localhost:8002/websocket
    application = Application([
        # Each endpoint connects clients with the services of a registry
        SnorkyWebSocketHandler.get_route(service_registry, "/websocket"),
    ])
    application.listen(8002, address="") # listen on all network interfaces

    try:
        print("Snorky running...")
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
