"use strict";

(function() {

  Snorky.Service = Snorky.Class({
    constructor: function(name, snorky) {
      if (!name instanceof String|| !snorky) {
        throw Error("Bad arguments for service constructor");
      }
      this.name = name;
      this.snorky = snorky;

      this.init();
    },

    init: function() {
      // noop
    },

    send: function(message) {
      this.snorky.send(this.name, message);
    },

    onMessage: function(message) {
      // noop
    }
  });

  Snorky.RPCService = Snorky.Class(Snorky.Service, {
    init: function() {
      this.nextCallId = 0;
      this.calls = {} // callId -> Promise
    },

    call: function(command, params) {
      var self = this;
      return new Promise(function(resolve, reject) {
        var callId = self.nextCallId++;
        self.calls[callId] = { "resolve": resolve, "reject": reject };

        self.send({
          "command": command,
          "params": params,
          "call_id": callId
        });
      })
    },

    onMessage: function(message) {
      if (!"type" in message) {
        console.error('Non-RPC message received from service "%s"',
                      this.name);
        return;
      }

      if (message.type == "response" || message.type == "error") {
        // Check for a known call_id
        if (!message.call_id in this.calls) {
          console.error(
            'Response for unknown call with id "%s" from service "%s"',
            message.call_id, this.name);
          return;
        }
      }

      if (message.type == "response") {
        this.calls[message.call_id].resolve(message.data);
      } else if (message.type == "error") {
        this.calls[message.call_id].reject(Error(message.message));
      } else {
        this.onNotification(message);
      }
    },

    onNotification: function(message) {
      // noop
    },

    STATIC: {
      addRPCMethods: function(methods) {
        // Convenience function to add RPC methods to the class

        var cls = this;
        _.each(methods, function(method) {
          cls.prototype[method] = function(params) {
            return this.call(method, params);
          };
        })
      }
    }
  })

})();
