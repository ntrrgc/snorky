(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.PubSub = new Class(Snorky.RPCService, {
    onNotification: function(message) {
      if (message.type == "message") {
        Snorky.emitEvent(this.onMessagePublished, message);
      } else {
        console.error("Unknown message type in messaging service: " +
                      message.type);
      }
    },

    onMessagePublished: function(message) {
      // noop
    }
  });
  Snorky.PubSub.addRPCMethods([
    "publish",
    "subscribe",
    "unsubscribe"
  ]);

})();
