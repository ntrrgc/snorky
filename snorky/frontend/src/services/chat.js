(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.Chat = new Class(Snorky.RPCService, {
    onNotification: function(message) {
      if (message.type == "message") {
        Snorky.emitEvent(this.onParticipantMessage, message);
      } else if (message.type == "presence") {
        Snorky.emitEvent(this.onPresence, message);
      } else if (message.type == "read") {
        Snorky.emitEvent(this.onRead, message);
      } else {
        console.error("Unknown message type in messaging service: " +
                      message.type);
      }
    },

    onParticipantMessage: function(message) {
      // noop
    },

    onPresence: function(presence) {
      // noop
    },

    onRead: function(event) {
      // noop
    }
  });
  Snorky.Chat.addRPCMethods([
    "join",
    "leave",
    "send",
    "read"
  ]);

})();

