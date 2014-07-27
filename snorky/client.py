from abc import abstractproperty, abstractmethod

class Client(object):
    def __init__(self):
        self.identity = None

    @abstractproperty
    def remote_address(self):
        pass

    @abstractmethod
    def send(self, msg):
        pass
