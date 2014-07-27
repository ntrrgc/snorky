(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.DataSync = new Class(Snorky.RPCService, {
    onNotification: function(message) {
      if (message.type == "delta") {
        Snorky.emitEvent(this.onDelta, message.delta);
      } else {
        console.error("Unknown message type in DataSync service: " +
                      message.type);
      }
    },

    onDelta: function(delta) {
      // noop
    }
  });
  Snorky.Messaging.addRPCMethods([
    "acquireSubscription",
    "cancelSubscription"
  ]);

})();

