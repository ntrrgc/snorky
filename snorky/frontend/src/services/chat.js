(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.Chat = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);

      this.notificationReceived.add(this.onNotification, this);

      this.participantMessageReceived = new Snorky.Signal();
      this.presenceReceived = new Snorky.Signal();
      this.readReceived = new Snorky.Signal();
    },

    onNotification: function(message) {
      if (message.type == "message") {
        this.participantMessageReceived.dispatch(message);
      } else if (message.type == "presence") {
        this.presenceReceived.dispatch(message);
      } else if (message.type == "read") {
        this.readReceived.dispatch(message);
      } else {
        console.error("Unknown message type in messaging service: " +
                      message.type);
      }
    }
  });
  Snorky.Chat.addRPCMethods([
    "join",
    "leave",
    "send",
    "read"
  ]);

})();

