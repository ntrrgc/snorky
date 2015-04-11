// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

(function() {
  "use strict";

  var Class = Snorky.Class;
  var _ = Snorky._;

  var Cursor = new Class({});

  var ForeignCursor = new Class(Cursor, {
    constructor: function(data) {
      _.assign(this, data);
    },

    isMine: false
  });

  var OwnCursor = new Class(Cursor, {
    constructor: function(document, data) {
      this.document = document;
      this.removed = false;
      _.assign(this, data);

      this.pendingPromiseCount = 1; // The create request is pending still
    },

    isMine: true,

    update: function(newData) {
      var self = this;
      var service = this.document.service;
      self.pendingPromiseCount += 1;

      _.subset(newData, ["position", "status"], function(key) {
        throw new Error("Can't update '" + key + "' of cursor.");
      });

      // Optimization: skip rpcCall if old data and new data are equal
      if (_.isEqualRight(this, newData)) {
        return new Promise(function(success) { success(); });
      } else {
        _.assign(this, newData);

        return service.rpcCall("updateCursor", {
          privateHandle: this.privateHandle,
          newData: newData
        }).then(function () {
          self.pendingPromiseCount -= 1;
        });
      }
    },

    remove: function() {
      var self = this;
      var service = this.document.service;
      self.pendingPromiseCount += 1;
      self.removed = true;

      delete service.ownCursors[self.privateHandle];
      _.removeOnField("privateHandle", this.document.cursors,
                      this.privateHandle);

      return service.rpcCall("removeCursor", {
        privateHandle: this.privateHandle
      }).then(function () {
        self.pendingPromiseCount -= 1;
      });
    },

    isSynchronized: function() {
      return this.pendingPromiseCount === 0;
    }
  });

  var Document = new Class({
    constructor: function(service, name, cursors) {
      this.service = service;
      this.name = name;

      this.cursors = _.map(cursors, function(cursor) {
        cursor.document = this;
        return new ForeignCursor(cursor);
      }, this);

      this.cursorAdded = new Snorky.Signal();
      this.cursorUpdated = new Snorky.Signal();
      this.cursorRemoved = new Snorky.Signal();
    },

    onCursorAdded: function(cursor) {
      var fatCursor = new ForeignCursor(cursor);
      this.cursors.push(fatCursor);

      this.cursorAdded.dispatch(fatCursor)
    },

    onCursorUpdated: function(cursor) {
      var fatCursor = _.replaceOnField("publicHandle", this.cursors,
                                       cursor);
      this.cursorUpdated.dispatch(fatCursor);
    },

    onCursorRemoved: function(cursor) {
      _.removeOnField("publicHandle", this.cursors, cursor);
      this.cursorRemoved.dispatch(cursor);
    },

    createCursor: function(params) {
      var handle = this.service.getFreePrivateHandle();

      var cursor = new Snorky.Cursors.OwnCursor(this, {
        privateHandle: handle,
        position: params.position,
        status: params.status
      });

      var promise = this.service.rpcCall("createCursor", {
        privateHandle: handle,
        document: this.name,
        position: params.position,
        status: params.status
      }).then(function(publicHandle) {
        cursor.publicHandle = publicHandle;
        cursor.pendingPromiseCount -= 1;
      });

      this.service.ownCursors[handle] = cursor;
      this.cursors.push(cursor);

      return [cursor, promise];
    }
  });

  Snorky.Cursors = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);

      this.notificationReceived.add(this.onNotification, this);

      this.documents = {};
      this.ownCursors = {};
    },

    join: function(params) {
      var self = this;
      return this.rpcCall("join", params)
        .then(function(documentData) {
          var name = params.document;
          var document = new Snorky.Cursors.Document(
            self, name, documentData.cursors);
          self.documents[stableStringify(name)] = document;
          return document;
        });
    },

    onNotification: function(notification) {
      var cursor = notification.cursor;
      var document = this.documents[stableStringify(cursor.document)];
      if (!document) {
        throw Error("Notification for unknown document: " +
                    stableStringify(notification.document));
      }

      if (notification.type == "cursorAdded") {
        document.onCursorAdded(cursor);
      } else if (notification.type == "cursorUpdated") {
        document.onCursorUpdated(cursor);
      } else if (notification.type == "cursorRemoved") {
        document.onCursorRemoved(cursor);
      }
    },

    getFreePrivateHandle: function() {
      if (_.keys(this.ownCursors).length > 100) {
        throw new Error("Too many cursors (thrown at client side)");
      }
      var handle;
      do {
        handle = Math.round(Math.random() * 255);
      } while (handle in this.ownCursors);
      return handle;
    }
  });

  Snorky.Cursors.Document = Document;
  Snorky.Cursors.Cursor = Cursor;
  Snorky.Cursors.ForeignCursor = ForeignCursor;
  Snorky.Cursors.OwnCursor = OwnCursor;

})();


