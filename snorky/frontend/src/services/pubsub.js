(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.PubSub = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);

      this.notificationReceived.add(this.onNotification);
      this.messagePublished = new Snorky.Signal();
    },

    onNotification: function(message) {
      if (message.type == "message") {
        this.messagePublished.dispatch(message);
      } else {
        console.error("Unknown message type in messaging service: " +
                      message.type);
      }
    }
  });
  Snorky.PubSub.addRPCMethods([
    "publish",
    "subscribe",
    "unsubscribe"
  ]);

})();
