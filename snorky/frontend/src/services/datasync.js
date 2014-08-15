(function() {
  "use strict";

  var Class = Snorky.Class;
  var _ = Snorky._;

  Snorky.DataSync = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);
      this.notificationReceived.add(this.onNotification, this);
      this.deltaReceived = new Snorky.Signal();
    },

    onNotification: function(message) {
      if (message.type == "delta") {
        this.deltaReceived.dispatch(message.delta);
      } else {
        console.error("Unknown message type in DataSync service: " +
                      message.type);
      }
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
    }
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
