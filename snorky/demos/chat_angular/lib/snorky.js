var Snorky = (function(Class) {
  "use strict";

  // Minimal lodash-style implementation
  var _ = {
    each: function(collection, callback, thisArg) {
      for (var key in collection) {
        if (callback.call(thisArg, collection[key], key, collection) === false) {
          break;
        }
      }
    },
    assign: function(object, source) {
      for (var key in source) {
        object[key] = source[key];
      }
      return object;
    }
  };

  var Snorky = new Class({
    constructor: function(socketClass, address, services, debug) {
      this.address = address;
      this.socketClass = socketClass;
      this.debug = (debug !== undefined ? debug : false);
      this.services = {};

      for (var serviceName in services) {
        var ServiceClass = services[serviceName];
        this.services[serviceName] = new ServiceClass(serviceName, this);
      }

      this._socket = null;
      this._queuedMessages = [];
      this.connected = false;
      this.connecting = false;

      this.connect();
    },

    logDebug: function() {
      // Do not use console.log when console is undefined (e.g. Internet
      // Explorer)
      if (this.debug && console && console.log)
      {
        // Use console.debug() falling back to console.log() if unavailable
        var debug = console.debug || console.log;

        if (debug.apply) {
          debug.apply(console, arguments);
        } else {
          // Some versions of IE do not have apply
          var a = arguments;
          debug(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9],
                a[10], a[11], a[12]);
        }
      }
    },

    connect: function() {
      var self = this;

      this.connecting = true;

      this._socket = new this.socketClass(this.address);
      this._socket.onopen = function() {
        self._onSocketOpen();
      };
      this._socket.onmessage = function(e) {
        self._onSocketMessage(e);
      };
      this._socket.onclose = function() {
        self._onSocketClose();
      };
    },

    disconnect: function() {
      this._socket.close();
      this._socket = null;
    },

    _onSocketOpen: function() {
      this.logDebug("Connected to Snorky server.");

      this.connected = true;
      this.connecting = false;

      Snorky.emitEvent(this.onConnected);

      _.each(this._queuedMessages, function(rawMessage) {
        this._socket.send(rawMessage);
      });
      this._queuedMessages = [];
    },

    _onSocketMessage: function(event) {
      var rawMessage = event.data;
      var packet = JSON.parse(rawMessage);
      var service = packet.service;
      if (service in this.services) {
        // TODO Refactor message to content?
        this.services[service].onMessage(packet.message);
      }
    },

    _onSocketClose: function() {
      this.logDebug("Snorky disconnected");

      this.connected = false;
      this.connecting = false;

      Snorky.emitEvent(this.onDisconnected);
    },

    _sendServiceMessage: function(serviceName, message) {
      var rawMessage = JSON.stringify({
        "service": serviceName,
        "message": message
      });

      if (this.connected) {
        this._socket.send(rawMessage);
      } else {
        this._queuedMessages.push(rawMessage);
      }
    },

    onConnected: function() {
      // noop
    },

    onDisconnected: function() {
      // noop
    }

  });

  // Export Class and _
  Snorky.Class = Class;
  Snorky._ = _;

  // Snorky will use ES6 promises by default, but it allows switching
  Snorky.Promise = Promise;

  // Some MV* frameworks need to envelop event handlers or perform additional
  // tasks in order to update the UI. By default we will just call the
  // function normally, but allow changing this to extensions.
  //
  // We will use this adapter for all events intended to be defined outside of
  // Snorky code.
  Snorky.emitEvent = function(callback) {
    var callbackArgs = Array.prototype.slice.call(arguments, 1);
    callback.apply(undefined, callbackArgs);
  };

  return Snorky;

})(my.Class);

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

      this.init();
    },

    init: function() {
      // noop
    },

    sendMessage: function(message) {
      this.snorky._sendServiceMessage(this.name, message);
    },

    onMessage: function(message) {
      // noop
    }
  });

  Snorky.RPCService = new Class(Snorky.Service, {
    init: function() {
      this.nextCallId = 0;
      this.calls = {}; // callId -> Promise
    },

    call: function(command, params) {
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

    onMessage: function(message) {
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
          // Prevent the user from breaking internal existing methods
          if (method in cls.prototype) {
            throw Error('Method "' + method + '" already exists in the ' +
                        'class. Refusing to overwrite it.');
          }

          cls.prototype[method] = function(params) {
            return this.call(method, params || {});
          };
        });
      }
    }
  });

})();

(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.Messaging = new Class(Snorky.RPCService, {
    onNotification: function(message) {
      if (message.type == "message") {
        Snorky.emitEvent(this.onParticipantMessage, message);
      } else {
        console.error("Unknown message type in messaging service: " +
                      message.type);
      }
    },

    onParticipantMessage: function(message) {
      // noop
    }
  });
  Snorky.Messaging.addRPCMethods([
    "registerParticipant",
    "unregisterParticipant",
    "listParticipants",
    "send"
  ]);

})();
