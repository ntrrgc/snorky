from snorky.backend import SnorkyBackend, SnorkyHTTPTransport, SnorkyError

backend_http = SnorkyHTTPTransport("http://localhost:8001/backend",
                                   key="swordfish")
backend = SnorkyBackend(backend_http)

response = backend.call("pubsub_backend", "publish",
                        channel="announcements", message="Hello World")
