// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

(function() {
  "use strict";

  var Class = Snorky.Class;
  var _ = Snorky._;

  Snorky.Service = new Class({
    constructor: function(name, snorky) {
      if (!name instanceof String|| !snorky) {
        throw Error("Bad arguments for service constructor");
      }
      this.name = name;
      this.snorky = snorky;

      this.packetReceived = new Snorky.Signal();

      this.init();
    },

    init: function() {
      // noop
    },

    sendMessage: function(message) {
      this.snorky._sendServiceMessage(this.name, message);
    }
  });

  Snorky.RPCService = new Class(Snorky.Service, {
    init: function() {
      this.nextCallId = 0;
      this.calls = {}; // callId -> Promise

      this.packetReceived.add(this.onPacket, this);
      this.notificationReceived = new Snorky.Signal();
    },

    rpcCall: function(command, params) {
      var self = this;
      return new Snorky.Promise(function(resolve, reject) {
        var callId = self.nextCallId++;
        self.calls[callId] = { "resolve": resolve, "reject": reject };

        self.sendMessage({
          "command": command,
          "params": params,
          "callId": callId
        });
      });
    },

    onPacket: function(message) {
      if (!("type" in message)) {
        console.error('Non-RPC message received from service "%s"',
                      this.name);
        return;
      }

      if (message.type == "response" || message.type == "error") {
        // Check for a known callId
        if (!(message.callId in this.calls)) {
          console.error(
            'Response for unknown call with id "%s" from service "%s"',
            message.callId, this.name);
          return;
        }
      }

      if (message.type == "response") {
        this.calls[message.callId].resolve(message.data);
      } else if (message.type == "error") {
        this.calls[message.callId].reject(Error(message.message));
      } else {
        this.notificationReceived.dispatch(message);
      }
    },

    STATIC: {
      addRPCMethods: function(methods) {
        // Convenience function to add RPC methods to the class

        var cls = this;
        _.each(methods, function(method) {
          // Prevent the user from breaking internal existing methods
          if (method in cls.prototype) {
            throw Error('Method "' + method + '" already exists in the ' +
                        'class. Refusing to overwrite it.');
          }

          cls.prototype[method] = function(params) {
            return this.rpcCall(method, params || {});
          };
        });
      }
    }
  });

})();
