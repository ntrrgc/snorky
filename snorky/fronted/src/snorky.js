var Snorky = (function(Class) {
  "use strict";

  // Minimal lodash-style implementation
  var _ = {
    each: function(collection, callback, thisArg) {
      for (var key in collection) {
        if (callback.call(thisArg, collection[key], key, collection) == false) {
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

  var Snorky = Class({
    STATIC: {
      Promise: Promise // use ES6 promises by default
    },

    constructor: function(socketClass, address, services, debug) {
      this.address = address;
      this.socketClass = socketClass;
      this.debug = (debug !== undefined ? debug : false);
      this.services = {};

      for (var serviceName in services) {
        var serviceClass = services[serviceName];
        this.services[serviceName] = new serviceClass(serviceName, this);
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
      if (this.debug && typeof console == "object") {
        console.debug.apply(console, arguments);
      }
    },

    connect: function(done) {
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
    }

  });

  // Export Class
  Snorky.Class = Class;

  return Snorky;

})(my.Class);
