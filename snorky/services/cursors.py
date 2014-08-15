from snorky.services.base import RPCService, RPCError, rpc_command
from snorky.types import values, items, MultiDict
import random


class Cursor(object):
    def __init__(self, handle, document, position, status, owner):
        self.handle = handle
        self.document = document
        self.position = position
        self.status = status
        self.owner = owner

    def for_json(self):
        return {
            "handle": self.handle,
            "document": self.document,
            "position": self.position,
            "status": self.status,
            "owner": self.owner.identity,
        }


class CursorsService(RPCService):
    def __init__(self, name):
        RPCService.__init__(self, name)

        self.clients_by_document = MultiDict()
        self.documents_by_client = MultiDict()
        self.cursors_by_document = MultiDict()
        self.cursors_by_client = {}

    def check_identity(self, client):
        if client.identity is None:
            raise RPCError("Not authenticated")

    @rpc_command
    def join(self, req, document):
        client = req.client
        self.check_identity(client)

        if self.clients_by_document.in_set(document, client):
            raise RPCError("Already joined")

        self.clients_by_document.add(document, client)
        self.documents_by_client.add(client, document)
        cursors = self.cursors_by_document.get_set(document)
        return {
            "cursors": [
                cursor.for_json()
                for cursor in cursors
            ]
        }

    @rpc_command
    def leave(self, req, document):
        client = req.client

        if not self.clients_by_document.in_set(document, client):
            raise RPCError("Not joined")

        self.do_leave(client, document)

    def check_new_cursor_allowed(self, client):
        # Limit to 16 cursors per client
        if len(self.cursors_by_client.get(client, {})) >= 16:
            raise RPCError("Too many cursors")

    @rpc_command
    def createCursor(self, req, document, position, status):
        client = req.client

        if not self.clients_by_document.in_set(document, client):
            raise RPCError("Not joined")

        self.check_new_cursor_allowed(client)

        # Pick a random, free handle
        while True:
            handle = random.getrandbits(16)
            if handle not in self.cursors_by_client.get(client, {}):
                break

        cursor = Cursor(handle, document, position, status, client)

        # Publish
        for other_client in self.clients_by_document.get_set(document):
            if other_client is client:
                continue
            self.send_message_to(other_client, {
                "type": "cursorAdded",
                "cursor": cursor.for_json(),
            })

        self.cursors_by_client.setdefault(client, {})
        self.cursors_by_client[client][handle] = cursor
        self.cursors_by_document.add(document, cursor)

        return handle

    @rpc_command
    def updateCursor(self, req, handle, newData):
        client = req.client

        if handle not in self.cursors_by_client.get(client, {}):
            raise RPCError("No such cursor")

        cursor = self.cursors_by_client[client][handle]

        if "position" in newData:
            cursor.position = newData["position"]
        if "status" in newData:
            cursor.status = newData["status"]

        # Publish
        for other_client in self.clients_by_document.get_set(cursor.document):
            if other_client is client:
                continue
            self.send_message_to(other_client, {
                "type": "cursorUpdated",
                "cursor": cursor.for_json(),
            })

    @rpc_command
    def removeCursor(self, req, handle):
        client = req.client

        if handle not in self.cursors_by_client.get(client, {}):
            raise RPCError("No such cursor")

        self.do_remove_cursor(client, handle)

    def do_remove_cursor(self, client, handle):
        cursor = self.cursors_by_client[client][handle]

        self.cursors_by_document.remove(cursor.document, cursor)

        del self.cursors_by_client[client][handle]
        if len(self.cursors_by_client[client]) == 0:
            del self.cursors_by_client[client]

        # Publish
        for other_client in self.clients_by_document.get_set(cursor.document):
            if other_client is client:
                continue
            self.send_message_to(other_client, {
                "type": "cursorRemoved",
                "cursor": {
                    "handle": handle
                }
            })

    def do_leave(self, client, document):
        # Get list of cursor handles belonging to the specified user and
        # document
        handles = [handle
                   for (handle, cursor)
                   in items(self.cursors_by_client.get(client, {}))
                   if cursor.document == document]

        for handle in handles:
            self.do_remove_cursor(client, handle)

        self.clients_by_document.remove(document, client)
        self.documents_by_client.remove(client, document)

    def client_disconnected(self, client):
        documents = list(self.documents_by_client.get_set(client))

        for document in documents:
            self.do_leave(client, document)
