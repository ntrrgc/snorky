// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

describe("ensureReturnsPromise", function() {
  it("turns nothing into fulfilled promise", function() {
    var testResolve = ensureReturnsPromise(function() {});

    var returnedPromise = testResolve();
    expect(returnedPromise.then).not.toBe(undefined);

    returnedPromise.then(function(value) {
      expect(value).toBe(undefined);
      done();
    }, function(error) {
      expect("promise").toBe("resolved");
      done();
    });
  });

  it("turns non-thenables into fulfilled promises", function() {
    var testResolve = ensureReturnsPromise(function() {
      return "Hi";
    });

    var returnedPromise = testResolve();
    expect(returnedPromise.then).not.toBe(undefined);

    returnedPromise.then(function(value) {
      expect(value).toEqual("Hi");
      done();
    }, function(error) {
      expect("promise").toBe("resolved");
      done();
    });
  });

  it("turns exceptions into rejected promises", function() {
    var testResolve = ensureReturnsPromise(function() {
      throw new Error("synchronous foo error");
    });

    var returnedPromise = testResolve();
    expect(returnedPromise.then).not.toBe(undefined);

    returnedPromise.then(function() {
      expect("promise").toBe("rejected");
      done();
    }, function(error) {
      expect(error.message).toEqual("synchronous foo error");
      done();
    });
  });

  it("passes through fulfilled promises", function() {
    var resolvedPromise = makeResolvedPromise("Hi")

    var testResolve = ensureReturnsPromise(function() {
      return resolvedPromise;
    });

    var returnedPromise = testResolve();
    expect(returnedPromise).toBe(resolvedPromise);

    returnedPromise.then(function(value) {
      expect(value).toEqual("Hi");
      done();
    }, function(error) {
      expect("promise").toBe("resolved");
      done();
    });
  });

  it("passes through rejected promises", function() {
    var rejectedPromise = makeRejectedPromise(new Error("foo error"))

    var testReject = ensureReturnsPromise(function() {
      return rejectedPromise;
    });

    var returnedPromise = testReject();
    expect(returnedPromise).toBe(rejectedPromise);

    returnedPromise.then(function() {
      expect("promise").toBe("rejected");
      done();
    }, function(error) {
      expect(error.message).toEqual("foo error");
      done();
    });
  });
});

describe("itP promises", function() {
  beforeEach(function() {
    this.testChainLevel = 0;
  });

  itP("pass successful synchronous tests", function() {
    expect(true).toEqual(true);
  });

  var successfulTest = itP("pass when return a fulfilled promise", function() {
    expect(this.testChainLevel).toEqual(0);
    this.testChainLevel++;
    return makeResolvedPromise(12);
  });

  var successfulTest2 = itP("supports dependencies", successfulTest,
  function() {
    expect(this.testChainLevel).toEqual(1);
    this.testChainLevel++;
    return makeResolvedPromise();
  });

  itP("supports nested dependencies", successfulTest2, function() {
    expect(this.testChainLevel).toEqual(2);
    return makeResolvedPromise();
  });

  // Expected failures
  return;
  itP("fail unsuccessful synchronous tests", function() {
    expect(true).toEqual(false);
  });

  itP("fail when return a rejected promise", function() {
    return makeRejectedPromise(new Error("foo error"));
  });

  var rejectedTest = itP("fail when an exception is throw", function() {
    throw new Error("foo error");
  });

  itP("fail if dependencies fail", rejectedTest, function() {
    expect("this code").toBe("never executed");
  });
});
