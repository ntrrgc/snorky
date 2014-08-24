"use strict";

describe("stableStringify", function() {
  it("should be stable", function() {
    var left = { "a": "foo" };
    left["b"] = "bar";

    var right = { "b": "bar" };
    right["a"] = "foo";

    expect(JSON.stringify(left)).not.toEqual(JSON.stringify(right));
    expect(stableStringify(left)).toEqual(stableStringify(right));
  });

  var compareStringify = function(obj) {
    expect(stableStringify(obj)).toEqual(JSON.stringify(obj));
  };

  it("should support string", function() {
    compareStringify("string");
  });

  it("should support numbers", function() {
    compareStringify(15);
    compareStringify(-3);
  });

  it("should support null", function() {
    compareStringify(null);
  });

  it("should support empty dict", function() {
    compareStringify({});
  });

  it("should support empty list", function() {
    compareStringify([]);
  });

  it("should support list with elements", function() {
    compareStringify([1, 2, 3, 4]);
  });

  it("should support list with complex elements", function() {
    compareStringify(["a", "b", {"c": {"d": 4}}]);
  });

  it("should not dirty", function() {
    var obj = {"a": "foo"};
    stableStringify(obj);
    expect(obj.__cycle__).toBe(undefined);
  });

  it("should not allow cycles", function() {
    var obj = {"a": "foo"};
    obj["b"] = obj;

    expect(function() {
      stableStringify(obj);
    }).toThrow(new CycleError());

    expect(obj.__cycle__).toBe(undefined);
  });
});
