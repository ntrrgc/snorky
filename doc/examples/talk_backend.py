import json
import requests

# Publish "Hello world"
response_obj = requests.post("http://localhost:8001/backend", headers={
    "X-Backend-Key": "swordfish",
    "Content-Type": "application/json",
    "Accept": "application/json",
}, data=json.dumps({
    "service": "pubsub_backend",
    "message": {
        "command": "publish",
        "params": {
            "channel": "announcements",
            "message": "Hello World",
        }
    }
}).encode("UTF-8"))
