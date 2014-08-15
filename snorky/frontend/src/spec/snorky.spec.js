"use strict";

describe("Snorky connector", function() {
  var snorky, socket, connected, disconnected;

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
      this.close = jasmine.createSpy();
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

    connected = spySignal(snorky.connected);
    disconnected = spySignal(snorky.disconnected);

    expect(this.MockSocket).toHaveBeenCalledWith("ws://localhost/");
    expect(snorky.isConnected).toBe(false);
    expect(snorky.isConnecting).toBe(true);

    socket = snorky._socket;
    expect(socket).toEqual(jasmine.any(this.MockSocket));
  }).fn;

  var connectionEstablished =
    it("acknowledges when the endpoint accepts the connection", function() {
    createsSocket.call(this);

    expect(connected).not.toHaveBeenCalled();
    socket.onopen();
    expect(connected).toHaveBeenCalled();

    expect(snorky.isConnected).toBe(true);
    expect(snorky.isConnecting).toBe(false);
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

    var packetReceived = spySignal(snorky.services.mockService.packetReceived);

    var packet = {
      "service": "mockService",
      "message": "Hello World"
    };
    socket.onmessage({ data: JSON.stringify(packet) });

    expect(packetReceived)
      .toHaveBeenCalledWith("Hello World")
  });

  it("acknowledges when the endpoint closes the connection", function() {
    connectionEstablished.call(this);

    expect(disconnected).not.toHaveBeenCalled();
    socket.onclose();
    expect(disconnected).toHaveBeenCalled();

    expect(snorky.isConnected).toBe(false);
    expect(snorky.isConnecting).toBe(false);
  });

  it("is set to disconnected when closed in the client side", function() {
    connectionEstablished.call(this);

    snorky.disconnect();

    expect(snorky.isConnected).toBe(false);
    expect(snorky.isConnecting).toBe(false);
  });
});
