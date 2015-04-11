// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

angular.module("Snorky", [])
  .run(function($timeout) {
    // Run $digest on events
    var OldSignal = Snorky.Signal;
    Snorky.Signal = function() {
      OldSignal.apply(this, arguments);

      var oldDispatch = this.dispatch;
      this.dispatch = function() {
        var self = this;
        var args = arguments;
        $timeout(function() {
          oldDispatch.apply(self, args);
        }, 0);
      }
    };
    Snorky.Signal.prototype = new OldSignal();
    Snorky.Signal.prototype.constructor = Snorky.Signal;
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
