import math
from snorky.services.base import RPCService, rpc_command

class CalculatorService(RPCService):
    @rpc_command
    def sum(self, req, number1, number2):
        return number1 + number2

    @rpc_command
    def log(self, req, number, base=2.718):
        return math.log(number, base)
