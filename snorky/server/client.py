from abc import abstractproperty, abstractmethod
import json

class Client(object):
    def __init__(self):
        self.identity = None

    @abstractproperty
    def remote_address(self):
        pass

    @abstractmethod
    def send(self, msg):
        pass

class TornadoClient(Client):
    def __init__(self, req_handler):
        super(TornadoClient, self).__init__()
        self.req_handler = req_handler

    def remote_address(self):
        return self.req_handler.request.remote_ip

    def send(self, msg):
        self.req_handler.write_message(json.dumps(msg))
