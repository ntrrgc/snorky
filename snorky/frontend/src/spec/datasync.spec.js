"use strict";

describe("DataSync service", function() {
  it("has RPC methods", function() {
    var proto = Snorky.DataSync.prototype;
    expect(proto.acquireSubscription).not.toBe(undefined);
    expect(proto.cancelSubscription).not.toBe(undefined);

    var datasync = new Snorky.DataSync("datasync", {})
    expect(datasync.acquireSubscription).not.toBe(undefined);
    expect(datasync.cancelSubscription).not.toBe(undefined);
  });
});

describe("CollectionDeltaProcessor", function() {
  var proc;
  var players;

  beforeEach(function() {
    players = [
      { id: 1, name: "Alice", color: "red" }
    ];
    proc = new Snorky.DataSync.CollectionDeltaProcessor({
      "Player": new Snorky.DataSync.ArrayCollection(players)
    });
  });

  it("has correct collections", function() {
    expect(proc.collections).not.toBe(undefined);
    expect(proc.collections["Player"]).not.toBe(undefined);
    expect(proc.collections["Player"] instanceof Snorky.DataSync.ArrayCollection)
        .toBe(true);
    expect(proc.collections["Player"] instanceof Snorky.DataSync.Collection)
        .toBe(true);
  });

  it("handles inserion deltas", function() {
    proc.processDelta({
      type: "insert",
      model: "Player",
      data: { id: 2, name: "Ted", color: "black" }
    });

    expect(players).toEqual([
      { id: 1, name: "Alice", color: "red" },
      { id: 2, name: "Ted", color: "black" }
    ]);
  });

  it("handles deletion deltas", function() {
    proc.processDelta({
      type: "delete",
      model: "Player",
      data: { id: 1, name: "Alice", color: "red" }
    });

    expect(players).toEqual([]);
  });

  it("handles update deltas", function() {
    proc.processDelta({
      type: "update",
      model: "Player",
      oldData: { id: 1, name: "Alice", color: "red" },
      newData: { id: 1, name: "Alice", color: "blue" }
    });

    expect(players).toEqual([
      { id: 1, name: "Alice", color: "blue" }
    ]);
  });

  it("handles tagged deltas", function() {
    proc = new Snorky.DataSync.CollectionDeltaProcessor({
      "Player": {
        "bluePlayers": new Snorky.DataSync.ArrayCollection(players)
      }
    });

    proc.processDelta({
      type: "insert",
      model: "Player",
      tag: "bluePlayers",
      data: { id: 2, name: "Bob", color: "blue" }
    });

    expect(players).toEqual([
      { id: 1, name: "Alice", color: "red" },
      { id: 2, name: "Bob", color: "blue" }
    ]);
  });
});
