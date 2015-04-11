// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
    },
    map: function(array, callback, thisArg) {
      var ret = [];
      _.each(array, function(val) {
        ret.push(callback.call(thisArg, val));
      });
      return ret;
    },
    keys: function(obj) {
      var keys = [];
      for (var k in obj) {
        keys.push(k);
      }
      return keys;
    },
    findIndex: function(array, callback, thisArg) {
      var ret;
      _.each(array, function(value, index) {
        if (callback.call(thisArg, value)) {
          ret = index;
          return false;
        }
      });
      return ret;
    },
    find: function(array, callback, thisArg) {
      var index = _.findIndex(array, callback, thisArg);
      if (index !== undefined) {
        return array[index];
      }
    },
    remove: function(array, callback, thisArg) {
      var removedItems = [];

      for (var i = 0; i < array.length; i++) {
        var value = array[i];
        if (callback.call(thisArg, value)) {
          removedItems.push(value);
          array.splice(i, 1);
          i--;
        }
      }

      return removedItems;
    },
    isArray: function(thing) {
      return Object.prototype.toString.call(thing) === "[object Array]";
    },
    indexOf: function(haystack, needle) {
      for (var i = 0; i < haystack.length; i++) {
        if (haystack[i] === needle) {
          return i;
        }
      }
      return -1;
    },
    in: function(haystack, needle) {
      // TODO: Rename to `contains`
      if (_.isArray(haystack)) {
        return _.indexOf(haystack, needle) != -1;
      } else {
        return (needle in haystack);
      }
    },
    subset: function(object, allowedKeys, errorFn) {
      errorFn = errorFn || function() {};
      _.each(object, function(value, key) {
        if (!_.in(allowedKeys, key)) {
          errorFn(key, value);
        }
      });
    },
    replace: function(array, newValue, callback, thisArg) {
      // Replaces elements that make callback() return true with `newValue`.
      var ret;
      _.each(array, function(value, index) {
        if (callback.call(thisArg, value)) {
          array[index] = newValue;
          ret = value;
        }
      });
      return ret;
    },
    field: function(fieldName, object) {
      // Returns a function that compares that takes an object as argument and
      // compares it to `object` on the field `fieldName`.
      return function(otherObject) {
        return otherObject[fieldName] == object[fieldName];
      };
    },
    replaceOnField: function(fieldName, array, newValue) {
      return _.replace(array, newValue, _.field(fieldName, newValue));
    },
    removeOnField: function(fieldName, array, needle) {
      _.remove(array, _.field(fieldName, needle));
    },
    isEqualRight: function(bigObject, smallObject) {
      for (var key in smallObject) {
        if (bigObject[key] !== smallObject[key]) {
          return false;
        }
      }
      return true;
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
