# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.services.base import RPCService, RPCError, rpc_command
from snorky.services.datasync.managers.dealer import DealerManager
from snorky.services.datasync.managers.subscription import SubscriptionManager
from snorky.services.datasync.subscription import \
        Subscription, SubscriptionItem
from snorky.services.datasync.delta import \
        InsertionDelta, UpdateDelta, DeletionDelta
from snorky.timeout import TornadoTimeoutFactory
from snorky.log import snorky_log
from snorky.types import is_string
import functools


class DataSyncBackend(RPCService):
    def __init__(self, name, frontend, timeout_interval=120,
                 timeout_factory=None):
        super(DataSyncBackend, self).__init__(name)

        self.frontend = frontend
        self.timeout_interval = timeout_interval
        self.timeout_factory = timeout_factory or TornadoTimeoutFactory

    @rpc_command
    def authorizeSubscription(self, req, items):
        """Requests a subscription authorization token.

        :param dict items: Subscription items to be authorized.

            Each item must be a dictionary with two properties: ``dealer`` and
            ``query``.
        """
        obj_items = []
        try:
            for item in items:
                dealer_name = item["dealer"]

                if not is_string(dealer_name):
                    raise RPCError("dealer should be a dealer name")
                elif dealer_name not in self.frontend.dm.dealers_by_name:
                    raise RPCError("No such dealer")

                obj_item = SubscriptionItem(dealer_name, item["query"])
                obj_items.append(obj_item)
        except KeyError as field:
            raise RPCError("Missing field %s" % field)

        subscription = Subscription(obj_items, self.frontend)
        token = self.frontend.sm.register_subscription(subscription)
        self.frontend.dm.connect_subscription(subscription)

        subscription._awaited_client_timeout = self.timeout_factory.call_later(
                self.timeout_interval, self.frontend.do_cancel_subscription,
                subscription)

        return token

    @rpc_command
    def publishDeltas(self, req, deltas):
        """Distributes one or more deltas to the appropriate dealers which, in
        turn, will distribute them to browser clients.

        :param list deltas: A list of deltas represented as dictionaries.
        """
        # deltas = [{
        #    "type": "insert",
        #    "model": "player",
        #    "data": { "color": "blue" }
        # }]
        obj_deltas = []
        try:
            for delta in deltas:
                snorky_log.info(delta)

                delta_type = delta["type"]
                model = delta["model"]
                if not is_string(model):
                    raise RPCError("model must be string")

                if delta_type == "insert":
                    obj_delta = InsertionDelta(model, delta["data"])
                elif delta_type == "delete":
                    obj_delta = DeletionDelta(model, delta["data"])
                elif delta_type == "update":
                    obj_delta = UpdateDelta(model, delta["newData"],
                                            delta["oldData"])
                else:
                    raise RPCError("Invalid delta type")

                obj_deltas.append(obj_delta)
        except KeyError:
            raise RPCError("Missing field")

        for delta_obj in obj_deltas:
            self.frontend.dm.deliver_delta(delta_obj)
