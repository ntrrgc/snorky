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
      }, this);
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

(function() {
  "use strict";

  var Class = Snorky.Class;
  var _ = Snorky._;

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
  Snorky.DataSync.addRPCMethods([
    "acquireSubscription",
    "cancelSubscription"
  ]);


  var CollectionDeltaProcessor = Snorky.DataSync.CollectionDeltaProcessor =
  new Class({
    constructor: function(collections) {
      this.collections = collections || {};
    },

    itemsAreEqual: function(item, other, delta) {
      return item.id == other.id;
    },

    processDelta: function(delta) {
      var collection;
      var iter, item;

      if (!(delta.model in this.collections)) {
        if (console && console.error) {
          console.error("Received delta for unregistered model: " +
                        delta.model);
        }
        return;
      }

      // There are two ways to register collections and models.
      //
      // Simple way:
      // collections = { "Player": new ArrayCollection(...) }
      //
      // Tagged way (in order to have several views of the same model):
      // collections = { "Player": {
      //   "redPlayers": new ArrayCollection(...),
      //   "bluePlayers": new ArrayCollection(...)
      // } }
      if (this.collections[delta.model] instanceof
          Snorky.DataSync.Collection)
      {
        collection = this.collections[delta.model];
      } else {
        // Expect a dictionary of tag -> collection
        if (!(delta.tag in this.collections[delta.model])) {
          if (console && console.error) {
            console.error("Received delta with unregistered tag: " +
                          delta.tag + " (model: " + delta.model + ")");
          }
          return;
        }
        collection = this.collections[delta.model][delta.tag];
      }

      // Apply the delta on the collection
      if (delta.type == "insert") {
        collection.insert(delta.data);
      } else if (delta.type == "update") {
        iter = collection.getIterator();
        while (iter.hasNext()) {
          item = iter.next();
          if (this.itemsAreEqual(item, delta.oldData)) {
            iter.update(delta.newData);
            break;
          }
        }
      } else if (delta.type == "delete") {
        iter = collection.getIterator();
        while (iter.hasNext()) {
          item = iter.next();
          if (this.itemsAreEqual(item, delta.data)) {
            iter.remove();
            break;
          }
        }
      } else {
        if (console && console.error) {
          console.error("Received delta of strange type: " + delta.type);
        }
      }
    }
  });

  /* Data container and iterator for array */

  var Collection = Snorky.DataSync.Collection = new Class({});

  var ArrayIterator = Snorky.DataSync.ArrayIterator =
  new Class({
    constructor: function(array, options) {
      this.array = array;
      this.options = options;
    },

    array: null,
    index: -1,
    deleted: false,
    options: {},

    hasNext: function() {
      var lastIndex = this.array.length - 1;
      return (this.index < lastIndex);
    },

    next: function() {
      if (!this.hasNext()) {
        throw new Error("Busted iterator");
      }
      this.deleted = false;
      return this.array[++this.index];
    },

    checkSafe: function() {
      if (this.deleted) {
        throw new Error("Iterator pointing to a deleted item! (call next())");
      } else if (this.index == -1) {
        throw new Error("Iterator not pointing to an item! (call next())");
      }
    },

    remove: function() {
      this.checkSafe();

      this.array.splice(this.index--, 1);
      this.deleted = true;
    },

    update: function(newVal) {
      this.checkSafe();

      this.array[this.index] = this.options.transformItem(newVal);
    }
  });


  var ArrayCollection = Snorky.DataSync.ArrayCollection =
  new Class(Collection, {
    constructor: function(array, options) {
      this.array = array;
      this.options = _.defaults(options, {
        transformItem: function(item) {
          return item;
        }
      });
    },

    array: null,
    options: {},

    insert: function(val) {
      var transformed = this.options.transformItem(val);
      this.array.push(transformed);
    },

    getIterator: function() {
      return new ArrayIterator(this.array, this.options);
    }
  });


  /* Virtual single-item collection and iterator */

  var SingleItemIterator = Snorky.DataSync.SingleItemIterator =
  new Class({
    constructor: function(collection) {
      this.fetched = false;
      this.collection = collection;
    },

    fetched: false,
    collection: null,

    hasNext: function() {
      return !this.fetched;
    },

    next: function() {
      if (this.fetched) {
        throw new Error("Busted iterator");
      }
      this.fetched = true;
      return this.collection.readHandler();
    },

    remove: function() {
      if (!this.fetched) {
        throw new Error("Iterator not pointing to an item! (call next())");
      }
      this.collection.removeHandler();
    },

    update: function(newVal) {
      if (!this.fetched) {
        throw new Error("Iterator not pointing to an item! (call next())");
      }
      this.collection.updateHandler(newVal);
    },
  });

  var SingleItemCollection = Snorky.DataSync.SingleItemCollection =
  new Class(Collection, {
    constructor: function(readHandler, updateHandler, removeHandler) {
      this.readHandler = readHandler;
      this.updateHandler = updateHandler;
      this.removeHandler = removeHandler || function () {};
    },

    item: null,

    insert: function(val) {
      if (console && console.error) {
        console.error("Received insert() request in SingleItemCollection");
      }
    },

    getIterator: function() {
      return new SingleItemIterator(this);
    }
  });

})();
