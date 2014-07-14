import sys
import json
import requests

def announce(message):
    response = requests.post("http://localhost:5800/backend", headers={
        "X-Backend-Key": "swordfish",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }, data=json.dumps({
        "service": "pubsub_backend",
        "message": {
            "command": "publish",
            "callId": 0,
            "params": {
                "channel": "announcements",
                "message": message
            }
        }
    }))

    if response.json()["message"]["type"] == "error":
        print("Error: %s" % response.json()["message"]["message"])
        sys.exit(2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s 'Message to be announced'" % sys.argv[0])
        sys.exit(1)

    announce(sys.argv[1])
