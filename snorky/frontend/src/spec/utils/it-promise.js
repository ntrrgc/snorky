function makeResolvedPromise(value) {
  return new Promise(function(success) {
    success(value);
  });
}

function makeRejectedPromise(errorValue) {
  return new Promise(function(success, error) {
    error(errorValue);
  });
}

function ensureReturnsPromise(callback) {
  return function() {
    try {
      var ret = callback.call(this);
      if (ret && ret.then) {
        return ret;
      } else {
        return makeResolvedPromise(ret);
      }
    } catch (error) {
      return makeRejectedPromise(error);
    }
  }
}

function itpBase(jasmineItFunction, description) {
  var dependency, testCase;
  if (arguments.length == 3) {
    dependency = function() {};
    testCase = arguments[2];
  } else {
    dependency = arguments[2];
    testCase = arguments[3];
  }

  dependency = ensureReturnsPromise(dependency);
  testCase = ensureReturnsPromise(testCase);

  var testCaseWithDependencies = function() {
    var self = this;
    return dependency.call(self).then(function() {
      return testCase.call(self);
    }, function(error) {
      console.log("Failed due to rejected dependency.");
      return makeRejectedPromise(error);
    });
  }

  jasmineItFunction(description, function(done) {
    var testPromise = testCaseWithDependencies.call(this);
    testPromise.then(function() {
      // Test promise fulfilled
      done();
    }, function(error) {
      // Test promise rejected
      expect("promise").toBe("fulfilled");
      console.log(error);
      done();
    });
  });

  return testCaseWithDependencies;
}

function makeRealArray(pseudoArray) {
  return Array.prototype.slice.call(pseudoArray);
}

function itP() {
  var args = makeRealArray(arguments);
  return itpBase.apply(undefined, [it].concat(args));
}
