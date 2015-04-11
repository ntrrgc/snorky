// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

function itP(description, itfn){
    it(description, function(done){
        var result = itfn(); // call the inner it
        if(result.then) { // if promise was returned
            result.then(done, function(e){
                expect("promise").toBe("resolved");
                console.log(e);
                done();
            }); // resolve means done, reject is a throw
        } else {
            done(); // synchronous
        }
    });
}

describe("Promises", function() {
  var self;
  this.promiseSuite = true;

  beforeEach(function() {
    self = this;

    self.promise = new Snorky.Promise(function(success, error) {
      self.success = success;
      self.error = error;
    });
  });

  it("call then callbacks on success", function(done) {
    var self = this;

    self.promise.then(function() {
      done();
    });

    self.success(42);
  });

  it("call catch callbacks on error", function(done) {
    var self = this;

    self.promise.catch(function() {
      done();
    });

    self.error(new Error("foo error"));
  });

  it("call then callbacks on error", function(done) {
    var self = this;

    self.promise.then(undefined, function() {
      done();
    });

    self.error(new Error("foo error"));
  });

  it("call then callbacks on error, when resolved first", function(done) {
    var self = this;

    self.error(new Error("foo error"));

    self.promise.then(undefined, function() {
      done();
    });
  });

  it("can resolve with rejected promises", function() {
    var self = this;

    self.success(new Promise(function(success, error) {
      error(new Error("foo error"));
    }));

    self.promise.then(function() {
      // Must not be fulfilled!
      expect("promise").toBe("not fulfilled");
      done();
    }, function() {
      done();
    });
  });

  it("reject when chained but not handled", function() {
    var self = this;

    self.success(new Promise(function(success, error) {
      error(new Error("foo error"));
    }));

    var chainedPromise = self.promise.then(function() {
      // Must not be fulfilled!
      expect("chained promise").toBe("not fulfilled");
    });

    chainedPromise.then(function() {
      // Must not be fulfilled!
      expect("promise").toBe("not fulfilled");
      done();
    }, function() {
      done();
    });
  });
});
