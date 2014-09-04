from tornado.ioloop import IOLoop
from tornado.web import Application
from snorky import ServiceRegistry

from snorky.request_handlers.http import BackendHTTPHandler
from snorky.request_handlers.websocket import SnorkyWebSocketHandler

from snorky.services.pubsub import PubSubService, PubSubBackend

class PrivatePubSub(PubSubService):
    def can_publish(self, client, channel):
        # Publishing is only allowed from the backend
        return False

if __name__ == "__main__":
    # Create separate service registries, providing separate interfaces to
    # services
    frontend_registry = ServiceRegistry()
    backend_registry = ServiceRegistry()

    # Create a PubSub service and register it in the frontend registry
    pubsub = PrivatePubSub("pubsub")
    frontend_registry.register_service(pubsub)

    # Create a PubSub backend service and register it in the backend registry
    pubsub_backend = PubSubBackend("pubsub_backend", pubsub)
    backend_registry.register_service(pubsub_backend)

    # Make frontend_registry attend requests from WebSocket through part 5800
    frontend_application = Application([
        SnorkyWebSocketHandler.get_route(frontend_registry, "/ws"),
    ])
    frontend_application.listen(5800)

    # Make backend_registry attend requests from HTTP through port 5801
    backend_application = Application([
        (r"/backend", BackendHTTPHandler, {
            "service_registry": backend_registry,
            "api_key": "swordfish"
        }),
    ])
    backend_application.listen(5801)

    try:
        print("Snorky running...")
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
