angular.module("Snorky", [])
  .run(function($rootScope) {
    // Run $digest on events
    Snorky.emitEvent = function(callback) {
      var callbackArgs = Array.prototype.slice.call(arguments, 1);
      $rootScope.$apply(function() {
        callback.apply(undefined, callbackArgs);
      });
    };
  })
  .run(function($q) {
    // Use Angular promises
    Snorky.Promise = function PromiseQAdapter(callback) {
      var q = $q.defer();
      var resolve = function(value) {
        return q.resolve(value);
      };
      var reject = function(reason) {
        return q.reject(reason);
      };

      callback(resolve, reject);
      return q.promise;
    };
  })
