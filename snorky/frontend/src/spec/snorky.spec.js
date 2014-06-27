"use strict";

describe("Snorky connector", function() {
  var snorky, socket;

  beforeEach(function() {
    var that = this;
    this.MockSocket = function() {
      if (!this instanceof that.MockSocket) {
        throw Error("Not called as constructor.")
      }

      this.send = jasmine.createSpy();
      this.onopen = function() { };
      this.onmessage = function() { };
      this.onclose = function() { };
    };

    this.MockService = Snorky.Class(Snorky.Service, {
      doSomething: function() {
        this.sendMessage({"do": "something"});
      }
    });
  });

  var createsSocket = it("creates a socket instance", function() {
    spyOn(this, "MockSocket").and.callThrough();
    snorky = new Snorky(this.MockSocket, "ws://localhost/", {
      "mockService": this.MockService
    });
    spyOn(snorky, "onConnected");
    spyOn(snorky, "onDisconnected");

    expect(this.MockSocket).toHaveBeenCalledWith("ws://localhost/");
    expect(snorky.connected).toBe(false);
    expect(snorky.connecting).toBe(true);

    socket = snorky._socket;
    expect(socket).toEqual(jasmine.any(this.MockSocket));
  }).fn;

  var connectionEstablished =
    it("acknowledges when the endpoint accepts the connection", function() {
    createsSocket.call(this);

    expect(snorky.onConnected).not.toHaveBeenCalled();
    socket.onopen();
    expect(snorky.onConnected).toHaveBeenCalled();

    expect(snorky.connected).toBe(true);
    expect(snorky.connecting).toBe(false);
  }).fn;

  it("sends messages to services", function() {
    connectionEstablished.call(this);

    expect(snorky.services.mockService).toEqual(jasmine.any(this.MockService));

    // Sanity checks
    expect(snorky._sendServiceMessage).not.toBe(undefined);
    expect(snorky.services.mockService.snorky).toBe(snorky);
    expect(snorky._socket).toEqual(jasmine.any(this.MockSocket));
    expect(snorky._socket.send).not.toBe(undefined);

    snorky.services.mockService.doSomething();

    expect(socket.send.calls.count()).toEqual(1);
    expect(JSON.parse(socket.send.calls.argsFor(0)[0])).toEqual({
      "service": "mockService",
      "message": {
        "do": "something"
      }
    });
  });

  it("receives messages from services", function() {
    connectionEstablished.call(this);

    spyOn(snorky.services.mockService, "onMessage");

    var packet = {
      "service": "mockService",
      "message": "Hello World"
    };
    socket.onmessage({ data: JSON.stringify(packet) });

    expect(snorky.services.mockService.onMessage)
      .toHaveBeenCalledWith("Hello World")
  });

  it("acknowledges when the endpoint closes the connection", function() {
    connectionEstablished.call(this);

    expect(snorky.onDisconnected).not.toHaveBeenCalled();
    socket.onclose();
    expect(snorky.onDisconnected).toHaveBeenCalled();

    expect(snorky.connected).toBe(false);
    expect(snorky.connecting).toBe(false);
  });
});
