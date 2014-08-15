describe("Messaging service", function() {
  beforeEach(function() {
    this.MockService = Snorky.Class(Snorky.Messaging, {
      constructor: function() {
        // Do not initialize snorky and name
        Snorky.Messaging.call(this, "mock", {});
      }
    });
    this.messagingService = new this.MockService();

    spyOn(this.messagingService, "sendMessage");
    participantMessageReceived = spySignal(this.messagingService.participantMessageReceived);
  });

  it("sends messages", function() {
    // Should work if RPC services work
    this.messagingService.send({
      sender: "Alice",
      dest: "Bob",
      body: "Hello"
    });

    expect(this.messagingService.sendMessage).toHaveBeenCalledWith({
      "command": "send",
      "callId": 0,
      "params": {
        sender: "Alice",
        dest: "Bob",
        body: "Hello"
      }
    });
  });

  it("receives messages", function() {
    this.messagingService.messageReceived.dispatch({
      "type": "message",
      "sender": "Bob",
      "dest": "Alice",
      "body": "Hi, Alice"
    });

    expect(participantMessageReceived).toHaveBeenCalledWith(
      jasmine.objectContaining({
        "sender": "Bob",
        "dest": "Alice",
        "body": "Hi, Alice"
      }));
  });
});
