"use strict";

describe("A Snorky RPC service", function() {
  beforeEach(function() {
    this.MockService = Snorky.Class(Snorky.RPCService, {
      constructor: function() {
        // Do not initialize snorky and name
        // Mock sendMessage method with an spy
        Snorky.RPCService.call(this, "mock", {});
        spyOn(this, "sendMessage");
      }
    });
    this.MockService.addRPCMethods(["sum"]);

    this.mockService = new this.MockService();
  });

  it("can not overwrite methods with .addRPCMethods()", function() {
    var self = this;

    var overrideInClass = function() {
      // already defined
      self.MockService.addRPCMethods(["sum"]);
    };
    var errorMsg1 = 'Method "sum" already exists in the class. ' +
      'Refusing to overwrite it.';

    var overrideInParents = function() {
      // defined in Service (super parent)
      self.MockService.addRPCMethods(["sendMessage"]);
    };
    var errorMsg2 = 'Method "sendMessage" already exists in the class. ' +
      'Refusing to overwrite it.';

    expect(overrideInClass).toThrow(Error(errorMsg1));
    expect(overrideInParents).toThrow(Error(errorMsg2));
  });

  it("can call known methods by their name", function() {
    expect(this.mockService.sum).toEqual(jasmine.any(Function));
  });

  it("can be requested commands", function(done) {
    var promise = this.mockService.sum({a: 1, b: 2});

    expect(this.mockService.sendMessage).toHaveBeenCalled();
    expect(this.mockService.sendMessage).toHaveBeenCalledWith(
      jasmine.objectContaining({
        "command": "sum",
        "params": {a: 1, b: 2}
      }));

    // The server replies
    this.mockService.onPacket({
      "type": "response",
      "data": 3,
      "callId": 0
    });

    promise.then(function(value) {
      expect(value).toBe(3);
      done();
    })
  });

  it("allows requesting commands without parameters", function() {
    this.mockService.sum();

    expect(this.mockService.sendMessage).toHaveBeenCalledWith({
      "command": "sum",
      "callId": 0,
      "params": {}
    });
  });
});
