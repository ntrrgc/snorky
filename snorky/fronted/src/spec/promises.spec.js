describe("Promises", function() {
  beforeEach(function() {
    var self = this;

    self.promise = new Promise(function(success, error) {
      self.success = success;
      self.error = error;
    });

    self.thenCallback = jasmine.createSpy("thenCallback");
    self.errorCallback = jasmine.createSpy("errorCallback");
  });

  it("call their callbacks", function(done) {
    var self = this;

    self.promise.then(self.thenCallback, self.errorCallback);
    expect(self.thenCallback).not.toHaveBeenCalled();
    expect(self.errorCallback).not.toHaveBeenCalled();

    self.success(42);

    setTimeout(function() {
      expect(self.thenCallback).toHaveBeenCalledWith(42);
      expect(self.errorCallback).not.toHaveBeenCalled();
      done();
    }, 0);
  });
});
