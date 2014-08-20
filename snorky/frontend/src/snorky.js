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
    },
    defaults: function(object, source) {
      object = object || {};
      for (var key in source) {
        if (!(key in object)) {
          object[key] = source[key];
        }
      }
      return object;
    }
  };

  var Snorky = new Class({
    constructor: function(socketClass, address, services, options) {
      options = options || {};
      this.address = address;
      this.socketClass = socketClass;
      this.debug = (options.debug !== undefined ? options.debug : false);
      this.services = {};

      for (var serviceName in services) {
        var ServiceClass = services[serviceName];
        this.services[serviceName] = new ServiceClass(serviceName, this);
      }

      this._socket = null;
      this._queuedMessages = [];
      this.isConnected = false;
      this.isConnecting = false;

      this.connected = new Snorky.Signal();
      this.disconnected = new Snorky.Signal();

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

      this.isConnecting = true;

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

      // Set as disconnected immediately
      this.isConnected = false;
    },

    _onSocketOpen: function() {
      this.logDebug("Connected to Snorky server.");

      this.isConnected = true;
      this.isConnecting = false;

      this.connected.dispatch();

      _.each(this._queuedMessages, function(rawMessage) {
        this._socket.send(rawMessage);
      }, this);
      this._queuedMessages = [];
    },

    _onSocketMessage: function(event) {
      var rawMessage = event.data;
      var packet = JSON.parse(rawMessage);
      var service = packet.service;
      if (service in this.services) {
        // TODO Refactor message to content?
        this.services[service].packetReceived.dispatch(packet.message);
      }
    },

    _onSocketClose: function() {
      this.logDebug("Snorky disconnected");

      this.isConnected = false;
      this.isConnecting = false;

      this.disconnected.dispatch();
      this._socket = null;
    },

    _sendServiceMessage: function(serviceName, message) {
      var rawMessage = JSON.stringify({
        "service": serviceName,
        "message": message
      });

      if (this.isConnected) {
        this._socket.send(rawMessage);
      } else {
        this._queuedMessages.push(rawMessage);
      }
    }

  });

  // Export Class and _
  Snorky.Class = Class;
  Snorky._ = _;

  // Export Signal class and allow replacing it
  if (typeof signals !== "undefined") {
    Snorky.Signal = signals.Signal;
  }

  // Snorky will use ES6 promises by default, but it allows switching
  Snorky.Promise = Promise;

  return Snorky;

})(my.Class);
