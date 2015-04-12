// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.PubSub = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);

      this.notificationReceived.add(this.onNotification, this);
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
