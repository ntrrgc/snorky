// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
    messageReceived = spySignal(this.messagingService.messageReceived);
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
    this.messagingService.packetReceived.dispatch({
      "type": "message",
      "sender": "Bob",
      "dest": "Alice",
      "body": "Hi, Alice"
    });

    expect(messageReceived).toHaveBeenCalledWith(
      jasmine.objectContaining({
        "sender": "Bob",
        "dest": "Alice",
        "body": "Hi, Alice"
      }));
  });
});
