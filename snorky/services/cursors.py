# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.services.base import RPCService, RPCError, rpc_command
from snorky.types import values, items, MultiDict
import random


class Cursor(object):
    def __init__(self, private_handle, public_handle, document, position,
                 status, owner):
        self.private_handle = private_handle
        self.public_handle = public_handle
        self.document = document
        self.position = position
        self.status = status
        self.owner = owner

    def for_json(self):
        return {
            "publicHandle": self.public_handle,
            "document": self.document,
            "position": self.position,
            "status": self.status,
            "owner": self.owner.identity,
        }


class CursorsService(RPCService):
    def __init__(self, name):
        RPCService.__init__(self, name)

        # (document : obj) -> set<Client>
        self.clients_by_document = MultiDict()
        # (Client) -> set<document : obj>
        self.documents_by_client = MultiDict()
        # (document : obj) -> dict<public_handle : int, Cursor>
        self.cursors_by_document = {}
        # (Client) -> dict<private_handle : int, Cursor>
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
        cursors = values(self.cursors_by_document.get(document, {}))
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
    def createCursor(self, req, privateHandle, document, position, status):
        client = req.client

        if not self.clients_by_document.in_set(document, client):
            raise RPCError("Not joined")

        if privateHandle in self.cursors_by_client.get(req.client, {}):
            raise RPCError("Reused handle")

        self.check_new_cursor_allowed(client)

        # Pick a random, free handle
        while True:
            handle = random.getrandbits(16)
            if handle not in self.cursors_by_client.get(client, {}):
                break

        cursor = Cursor(privateHandle, handle,
                        document, position, status, client)

        self.cursors_by_client.setdefault(client, {})
        self.cursors_by_client[client][privateHandle] = cursor
        self.cursors_by_document.setdefault(document, {})
        self.cursors_by_document[document][cursor.public_handle] = cursor

        # Publish
        for other_client in self.clients_by_document.get_set(document):
            if other_client is client:
                continue
            self.send_message_to(other_client, {
                "type": "cursorAdded",
                "cursor": cursor.for_json(),
            })

        return handle

    @rpc_command
    def updateCursor(self, req, privateHandle, newData):
        client = req.client

        if privateHandle not in self.cursors_by_client.get(client, {}):
            raise RPCError("No such cursor")

        cursor = self.cursors_by_client[client][privateHandle]

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
    def removeCursor(self, req, privateHandle):
        client = req.client

        if privateHandle not in self.cursors_by_client.get(client, {}):
            raise RPCError("No such cursor")

        self.do_remove_cursor(client, privateHandle)

    def do_remove_cursor(self, client, private_handle):
        cursor = self.cursors_by_client[client][private_handle]

        del self.cursors_by_document[cursor.document][cursor.public_handle]
        if len(self.cursors_by_document[cursor.document]) == 0:
            del self.cursors_by_document[cursor.document]

        del self.cursors_by_client[client][private_handle]
        if len(self.cursors_by_client[client]) == 0:
            del self.cursors_by_client[client]

        # Publish
        for other_client in self.clients_by_document.get_set(cursor.document):
            if other_client is client:
                continue
            self.send_message_to(other_client, {
                "type": "cursorRemoved",
                "cursor": {
                    "publicHandle": cursor.public_handle,
                    "document": cursor.document,
                },
            })

    def do_leave(self, client, document):
        # Get list of cursor handles belonging to the specified user and
        # document
        handles = [private_handle for (private_handle, cursor)
                   in items(self.cursors_by_client.get(client, {}))
                   if cursor.document == document]

        for private_handle in handles:
            self.do_remove_cursor(client, private_handle)

        self.clients_by_document.remove(document, client)
        self.documents_by_client.remove(client, document)

    def client_disconnected(self, client):
        documents = list(self.documents_by_client.get_set(client))

        for document in documents:
            self.do_leave(client, document)
