"use strict";

describe("A Snorky RPC service", function() {
  beforeEach(function() {
    this.MockService = Snorky.Class(Snorky.RPCService, {
      constructor: function() {
        // Do not initialize snorky and name
        // Mock send method with an spy
        spyOn(this, "send");
        this.init();
      }
    });
    this.MockService.addRPCMethods(["sum"]);

    this.mockService = new this.MockService();
  });

  it("can call known methods by their name", function() {
    expect(this.mockService.sum).toEqual(jasmine.any(Function));
  });

  it("can be requested commands", function() {
    var promise = this.mockService.sum({a: 1, b: 2});
    expect(promise.then).not.toBe(undefined);

    expect(this.mockService.send).toHaveBeenCalled();
    expect(this.mockService.send).toHaveBeenCalledWith(
      jasmine.objectContaining({
        "command": "sum",
        "params": {a: 1, b: 2}
      }));

  });
});
