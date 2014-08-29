(function() {
  "use strict";

  describe("Cursors service", function() {

    var Cursors = Snorky.Cursors;
    var Document = Snorky.Cursors.Document;
    var Cursor = Snorky.Cursors.Cursor;
    var OwnCursor = Snorky.Cursors.OwnCursor;
    var ForeignCursor = Snorky.Cursors.ForeignCursor;
    var _ = Snorky._;

    beforeEach(function() {
      this.service = new Cursors("cursors", {});
      var self = this;
      spyOn(this.service, "rpcCall").and.callFake(function() {
        return new Promise(function(success, error) {
          self.callPromise = { success: success, error: error };
        });
      });
    });

    it("can be constructed", function() {
      expect(this.service).not.toBe(undefined);
    });

    var joinDocument = itP("can join documents", function() {
      var self = this;
      expect(this).not.toBe(undefined);
      var promise = this.service.join({ document: "Sheet1" });

      expect(this.service.rpcCall).toHaveBeenCalledWith("join", {
        document: "Sheet1"
      });

      expect(this.callPromise.success).not.toBe(undefined);
      this.callPromise.success({
        "cursors": [{
          handle: 1,
          document: "Sheet1",
          position: 12,
          status: "read"
        }]
      });

      return promise.then(function(doc) {
        expect(doc instanceof Document).toBe(true);
        expect(doc.service).toBe(self.service);
        expect(doc.name).toEqual("Sheet1");

        expect(doc.foreignCursors.length).toEqual(1);
        var cursor = doc.foreignCursors[0];
        expect(cursor instanceof Cursor).toBe(true);
        expect(cursor instanceof ForeignCursor).toBe(true);
        expect(cursor.handle).toEqual(1);
        expect(cursor.position).toEqual(12);
        expect(cursor.status).toEqual("read");
        expect(cursor.document).toBe(doc);
        expect(cursor.isMine).toBe(false);

        self.document = doc;
      });
    });

    var createCursor = itP("can create cursors", joinDocument, function() {
      expect(this).not.toBe(undefined);
      expect(this.document).not.toBe(undefined);
      expect(this.document.createCursor).not.toBe(undefined);

      var ret = this.document.createCursor({
        position: 23,
        status: "read"
      });
      var cursor = ret[0], promise = ret[1];

      // The cursor is created immediately
      expect(cursor instanceof Cursor).toBe(true);
      expect(cursor instanceof OwnCursor).toBe(true);
      expect(cursor.position).toEqual(23);
      expect(cursor.status).toEqual("read");
      expect(cursor.pendingPromiseCount).toEqual(1);
      expect(cursor.isSynchronized()).toEqual(false);
      expect(cursor.isMine).toEqual(true);
      expect(cursor.removed).toEqual(false);
      expect(cursor.publicHandle).toBe(undefined);
      expect(cursor.privateHandle).not.toBe(undefined);
      expect(this.service.ownCursors[cursor.privateHandle]).toBe(cursor);
      this.cursor = cursor;

      // The RPC call has been made
      expect(this.service.rpcCall).toHaveBeenCalledWith("createCursor", {
        privateHandle: cursor.privateHandle,
        document: "Sheet1",
        position: cursor.position,
        status: cursor.status
      });

      // Snorky creates the cursor and replies with the public handle
      this.callPromise.success(50);

      return promise.then(function(val) {
        expect(val).toBe(undefined);
        expect(cursor.publicHandle).toEqual(50);
        expect(cursor.pendingPromiseCount).toEqual(0);
      });
    });

    itP("can update cursor", createCursor, function() {
      expect(this).not.toBe(undefined);
      expect(this.cursor).not.toBe(undefined);
      expect(this.cursor.pendingPromiseCount).toEqual(0);
      expect(this.cursor.document).not.toBe(undefined);
      expect(this.cursor.document.service).toBe(this.service);
      expect(this.cursor.document.service.rpcCall).not.toBe(undefined);

      var cursor = this.cursor;
      var promise = cursor.update({ position: 24 });

      // Position is changed immediately
      expect(cursor.position).toEqual(24);
      // Status is unchanged
      expect(cursor.status).toEqual("read");
      // Promise count has increased
      expect(cursor.pendingPromiseCount).toEqual(1);

      expect(this.service.rpcCall).toHaveBeenCalledWith("updateCursor", {
        privateHandle: cursor.privateHandle,
        newData: { position: 24 }
      });

      this.callPromise.success(null);

      return promise.then(function() {
        expect(cursor.pendingPromiseCount).toEqual(0);
      });
    });

    itP("can delete cursor", createCursor, function() {
      var cursor = this.cursor;
      var promise = cursor.remove();

      expect(cursor.pendingPromiseCount).toEqual(1);
      expect(cursor.removed).toEqual(true);
      expect(this.service.ownCursors[cursor.privateHandle]).toBe(undefined);

      expect(this.service.rpcCall).toHaveBeenCalledWith("removeCursor", {
        privateHandle: cursor.privateHandle
      });

      this.callPromise.success();

      return promise.then(function() {
        expect(cursor.pendingPromiseCount).toEqual(0);
      });
    });

  });
})();
