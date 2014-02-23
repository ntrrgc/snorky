import tornado.web
import simplejson as json
from tornado.log import gen_log
from tornado.web import Application
from miau.server.client import Client
from miau.server.managers.subscription import UnknownSubscription
from miau.common.forcejson import fstr


class JSONError(Exception):
    def __init__(self, status_code, reason, details=None, *args):
        self.status_code = status_code
        self.reason = reason
        if details:
            self.details = details % args
        else:
            self.details = None
    
    def jsonify(self, extra={}):
        data = {
            'type': 'error',
            'status_code': self.status_code,
            'reason': self.reason,
        }
        if self.details:
            data['details'] = self.details
        data.update(extra)
        return json.dumps(data)
    

class FrontendHandler(object):
    def __init__(self, facade):
        self.facade = facade
    
    def get_json_request(self, message):
        try:
            return json.loads(message, encoding="UTF-8")
        except ValueError:
            raise JSONError(400, "Bad Request")

    def send_error(self, ex):
        if ex.details:
            detail_str = " (%s)" % ex.details
        else:
            detail_str = ""

        msg = "Frontend: {code} {reason}{details} Message: {message}".\
                format(code=ex.status_code, message=self.message,
                       reason=ex.reason, details=detail_str)

        gen_log.error(msg)
        extra = {"call_id": self.call_id} if self.call_id else {}
        self.write_message(ex.jsonify(extra))

    def treat_errors(on_message):
        def on_message_with_errors(self, message):
            self.message = message
            self.call_id = None
            try:
                on_message(self, message)
            except JSONError as ex:
                self.send_error(ex)
            except (KeyError, TypeError):
                self.send_error(JSONError(422, "Unprocessable Entity"))
        return on_message_with_errors

    allowed_methods = ('acquire_subscription', 'cancel_subscription')

    def open(self):
        self.client = Client(self)

    def on_close(self):
        self.facade.client_disconnected(self.client)
    
    @treat_errors
    def on_message(self, message):
        r = self.get_json_request(message)
        self.call_id = r["call_id"]
        function = r["function"]

        if function in self.allowed_methods:
            # Remove "header" parameters
            del r["call_id"]
            del r["function"]

            # Call function
            response = getattr(self, function)(**r)

            # Add response header parameters
            response["type"] = "function_response"
            response["call_id"] = self.call_id

            # Send response
            self.write_message(json.dumps(response))
        else:
            raise JSONError(404, 'Not Found')

    def acquire_subscription(self, token):
        fstr(token)

        try:
            self.facade.acquire_subscription(self.client, token)
            return {'status_code': 204}
        except UnknownSubscription:
            raise JSONError(422, "Unprocessable Entity",
                    'Unknown Subscription: token=%s', token)

    def cancel_subscription(self, token):
        fstr(token)

        try:
            self.facade.cancel_subscription(self.client, token)
            return {'status_code': 204}
        except UnknownSubscription:
            raise JSONError(422, "Unprocessable Entity",
                    'Unknown Subscription: token=%s', token)
