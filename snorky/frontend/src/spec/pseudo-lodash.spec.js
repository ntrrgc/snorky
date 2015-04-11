describe("_.replace", function() {
  var _ = Snorky._;

  it("finds and replaces elements", function() {
    var array = [
      { id: 1, color: "red" },
      { id: 2, color: "blue" }
    ];
    var updatedElement = { id: 1, color: "green" };
    var ret = _.replace(array, updatedElement, function(e) {
      return e.id == updatedElement.id;
    });
    expect(array).toEqual([
      { id: 1, color: "green" },
      { id: 2, color: "blue" }
    ]);
  });
});

describe("_.field", function() {
  var _ = Snorky._;

  it("makes replace searches a bit shorter", function() {
    var array = [
      { id: 1, color: "red" },
      { id: 2, color: "blue" }
    ];
    var updatedElement = { id: 1, color: "green" };
    var ret = _.replace(array, updatedElement, _.field("id", updatedElement));
    expect(array).toEqual([
      { id: 1, color: "green" },
      { id: 2, color: "blue" }
    ]);
  });
});

describe("_.replaceOnField", function() {
  var _ = Snorky._;

  it("makes replace searches even shorter", function() {
    var array = [
      { id: 1, color: "red" },
      { id: 2, color: "blue" }
    ];
    var oldItem = array[0];
    var updatedElement = { id: 1, color: "green" };
    var ret = _.replaceOnField("id", array, updatedElement);
    expect(ret).toBe(oldItem);
    expect(array).toEqual([
      { id: 1, color: "green" },
      { id: 2, color: "blue" }
    ]);
  });
});

describe("_.removeOnField", function() {
  var _ = Snorky._;

  it("removes objects matching a needle in a certain field", function() {
    var array = [
      { id: 1, color: "red" },
      { id: 2, color: "blue" }
    ];
    var updatedElement = { id: 1, color: "green" };
    var ret = _.removeOnField("id", array, { id: 1 });
    expect(array).toEqual([
      { id: 2, color: "blue" }
    ]);
  });
});
