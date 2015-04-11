// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

"use strict";

var Class = my.Class;

describe("Classy classes", function() {
  it("creates simple classes", function() {
    var Car = Class({
      constructor: function(color) {
        this.color = color || "red";
      }
    });

    var redCar = new Car();
    expect(redCar.color).toBe("red");

    var blueCar = new Car("blue");
    expect(blueCar.color).toBe("blue");
  });

  it("creates classes with prototypical methods", function() {
    var Car = Class({
      constructor: function(color) {
        this.color = color || "red";
      },

      tellMyColor: function() {
        return "My color is " + this.color;
      }
    });

    var car = new Car();

    expect(car.tellMyColor()).toBe("My color is red");
    expect(car.tellMyColor).toBe(Car.prototype.tellMyColor);
  });

  it("crates inherited classes", function() {
    var Vehicle = Class({
      constructor: function(color) {
        this.color = color || "red";
      },

      vehicleFun: function() {
        return "I'm a vehicle";
      }
    });

    var RoadVehicle = Class(Vehicle, {
      constructor: function(color, numWheels) {
        RoadVehicle.Super.call(this, color);

        this.numWheels = numWheels;
      },

      roadFun: function() {
        return "I'm a road vehicle";
      }
    });

    var bike = new RoadVehicle("blue", 2);
    expect(bike.color).toBe("blue");
    expect(bike.numWheels).toBe(2);
    expect(bike.vehicleFun()).toBe("I'm a vehicle");
    expect(bike.roadFun()).toBe("I'm a road vehicle");
  });

  it("inherits constructors by default", function() {
    var A = Class({
      constructor: function() {
        this.foo = "bar";
      }
    });

    var B = Class(A, {
      getFoo: function() {
        return this.foo;
      }
    });

    var b = new B();
    expect(b.foo).toEqual("bar")
    expect(b.getFoo()).toEqual("bar")
  });

  it("works with instanceof", function() {
    var A = Class({});

    var a = new A();

    expect(a instanceof A).toEqual(true);
  });

  it("works with instanceof and new", function() {
    var A = new Class({});

    var a = new A();

    expect(a instanceof A).toEqual(true);
  });

  it("works with instanceof and constructors", function() {
    var A = Class({
      constructor: function() {
        this.foo = "bar";
      }
    });

    var a = new A();
    expect(a.foo).toEqual("bar");

    expect(a instanceof A).toEqual(true);
  });
});
