describe("Promises", function() {
  beforeEach(function() {
    var self = this;

    self.promise = new Promise(function(success, error) {
      self.success = success;
      self.error = error;
    });
  });

  it("call their callbacks", function(done) {
    var self = this;

    self.promise.then(function() {
      done();
    });

    self.success(42);
  });
});
