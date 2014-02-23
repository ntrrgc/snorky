import base64
import simplejson as json
from miau.common.delta import Delta, DeltaItemCreation, DeltaItemUpdate, \
        DeltaItemDeletion
from miau.server.subscription import SubscriptionItem
from miau.server.facade import Facade
from miau.common.forcejson import fstr
from tornado.web import Application, RequestHandler, HTTPError
from tornado.ioloop import IOLoop

from miau.server.managers.dealer import DealerManager, UnknownDealer
from miau.server.managers.subscription import SubscriptionManager

# base64.decodestring is deprecated in favor of decodebytes, which does exactly
# the same thing.
import sys
if sys.version_info < (3,0):
    base64.decodebytes = base64.decodestring

class UnprocessableEntity(HTTPError):
    def __init__(self, handler, details=None, *args, **kwargs):
        body = handler.request.body
        log_text = "Unprocessable entity: %s" % body
        if details:
            detail_str = details % args
            log_text += "\nDetails: %s" % detail_str

            handler.error_details = detail_str

        super(UnprocessableEntity, self).__init__(422, log_text, reason=
                "Unprocessable Entity", **kwargs)


class BackendRequestHandler(RequestHandler):
    def __init__(self, application, request, backend, facade, *args, **kwargs):
        super(BackendRequestHandler, self).__init__(
                application, request, *args, **kwargs)
        self.backend = backend
        self.facade = facade

    def get_json_request(self):
        # Throw an error if Content-Type is wrong
        # No Content-Type is accepted, but if it is present, it must be
        # 'application/json'. If an encoding is appended it must be UTF-8, i.e.
        # 'application/json; encoding=UTF-8'.
        ce = self.request.headers.get("Content-Type")
        if ce is None:
            pass
        elif not ce.startswith("application/json"):
            raise HTTPError(415, "Invalid Content-Type (%s). Body: %s",
                    ce, self.request.body)
        else:
            params = {name.strip(): value.strip()
                      for (name, value) in (x.split('=')
                                            for x in ce.split(';')[1:])}
            if params.get("encoding", "UTF-8") != "UTF-8":
                raise HTTPError(415,
                        "Invalid encoding (%s). Please use UTF-8",
                        params["UTF-8"])

        try:
            return json.loads(self.request.body, encoding="UTF-8")
        except ValueError:
            raise HTTPError(400, "Invalid syntax: %s", self.request.body)

    def write_error(self, status_code, **kwargs):
        data = {
            "status_code": status_code,
            "reason": self._reason,
        }
        if hasattr(self, "error_details"):
            data["details"] = self.error_details
        
        self.write(data)

    def compute_etag(self):
        return None # No cache, please.

    def _execute_method(self):
        if not self._finished:
            # Check authentication token
            auth_header = self.request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Basic '):
                auth_decoded = base64.decodebytes(auth_header[6:].encode())
                username, password = auth_decoded.decode().split(':', 2)
                
                # Secret key should be specified in the username field
                if username == self.backend.secret_key and password == '':
                    # Authorized
                    return super(BackendRequestHandler, self)._execute_method()

            # Not authorized
            self.request_auth()
    
    def request_auth(self):
        self.set_header('WWW-Authenticate', 'Basic realm=Backend key')
        raise HTTPError(401, "Unauthorized")
    

class SubscriptionHandler(BackendRequestHandler):
    def post(self):
        r = self.get_json_request()
        try:
            items = [
                SubscriptionItem(
                    fstr(i["dealer_name"]),
                    i["model_key"])
                for i in r["items"]
            ]
        except (KeyError, TypeError):
            raise UnprocessableEntity(self)

        # Authorize subscription
        try:
            token = self.facade.authorize_subscription(items)
        except UnknownDealer as ex:
            raise UnprocessableEntity(self, "Unknown dealer: %s",
                    ex.dealer_name)

        # Send token
        self.set_status(201)
        self.write({"token": token})


class NotifyDeltaHandler(BackendRequestHandler):
    def post(self):
        r = self.get_json_request()
        try:
            created = [
                DeltaItemCreation(fstr(x["model_class_name"]), x["data"])
                for x in r["created"]
            ]
            updated = [
                DeltaItemUpdate(fstr(x["model_class_name"]), x["old_data"],
                    x["new_data"])
                for x in r["updated"]
            ]
            deleted = [
                DeltaItemDeletion(fstr(x["model_class_name"]), x["data"])
                for x in r["deleted"]
            ]
        except (KeyError, TypeError):
            raise UnprocessableEntity(self)

        delta = Delta(created, updated, deleted)
        self.facade.deliver_delta(delta)

        self.set_status(204) # No Content


class Backend(Application):
    def __init__(self, facade, secret_key):
        self.secret_key = secret_key

        handler_params = {
            'facade': facade,
            'backend': self,
        }

        super(Backend, self).__init__([
            ('/subscription', SubscriptionHandler, handler_params),
            ('/notify_delta', NotifyDeltaHandler, handler_params),
        ])
