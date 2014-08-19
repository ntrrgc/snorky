#!/usr/bin/env python
import logging
from tornado.web import Application
from tornado.ioloop import IOLoop
from snorky.services.datasync import DataSyncService, DataSyncBackend
from snorky.services.datasync.dealers import BroadcastDealer
from snorky.request_handlers.websocket import SnorkyWebSocketHandler
from snorky.request_handlers.http import BackendHTTPHandler
from snorky import ServiceRegistry


#-----------------------------------------------------------------------------#
# Dealers (model classes and filters)                                         #
#-----------------------------------------------------------------------------#

class AllTodos(BroadcastDealer):
    name = "AllTasks"
    model = "Task"

#-----------------------------------------------------------------------------#
# Server startup                                                              #
#-----------------------------------------------------------------------------#
if __name__ == "__main__":
    # Create two services
    datasync = DataSyncService("datasync", [AllTodos])
    datasync_backend = DataSyncBackend("datasync_backend", datasync)

    logging.basicConfig(level=logging.INFO)

    # Register the frontend and backend services in different handlers
    frontend = ServiceRegistry([datasync])
    backend = ServiceRegistry([datasync_backend])

    # Create a WebSocket frontend
    app_frontend = Application([
        SnorkyWebSocketHandler.get_route(frontend, "/ws"),
    ])
    app_frontend.listen(5001)

    # Create a backend, set a secret key, port and address
    app_backend = Application([
        ("/backend", BackendHTTPHandler, {
            "service_registry": backend,
            "api_key": "swordfish"
        })
    ])
    app_backend.listen(5002)

    # Start processing
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
