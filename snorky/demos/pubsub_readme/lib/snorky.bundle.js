/*! Snorky JS connector (bundle) | http://snorkyproject.org/ | MPL License
 *  Includes other software:
 *   - my.class.js | https://github.com/jiem/my-class | MIT License
 *   - js-signals | http://millermedeiros.github.io/js-signals/ | MIT License *//*globals define:true, window:true, module:true*/
(function () {
  // Namespace object
  var my = {};
  // Return as AMD module or attach to head object
  if (typeof define !== 'undefined')
    define([], function () {
      return my;
    });
  else if (typeof window !== 'undefined')
    window.my = my;
  else
    module.exports = my;

  //============================================================================
  // @method my.Class
  // @params body:Object
  // @params SuperClass:function, ImplementClasses:function..., body:Object
  // @return function
  my.Class = function () {

    var len = arguments.length;
    var body = arguments[len - 1];
    var SuperClass = len > 1 ? arguments[0] : null;
    var hasImplementClasses = len > 2;
    var Class, SuperClassEmpty;

    if (body.constructor === Object) {
      if (SuperClass === null) {
        Class = function() { };
      } else {
        Class = function() {
          SuperClass.apply(this, arguments);
        };
      }
    } else {
      Class = body.constructor;
      delete body.constructor;
    }

    if (SuperClass) {
      SuperClassEmpty = function() {};
      SuperClassEmpty.prototype = SuperClass.prototype;
      Class.prototype = new SuperClassEmpty();
      Class.prototype.constructor = Class;
      Class.Super = SuperClass;
      extend(Class, SuperClass, false);
    }

    if (hasImplementClasses)
      for (var i = 1; i < len - 1; i++)
        extend(Class.prototype, arguments[i].prototype, false);

    extendClass(Class, body);

    return Class;

  };

  //============================================================================
  // @method my.extendClass
  // @params Class:function, extension:Object, ?override:boolean=true
  var extendClass = my.extendClass = function (Class, extension, override) {
    if (extension.STATIC) {
      extend(Class, extension.STATIC, override);
      delete extension.STATIC;
    }
    extend(Class.prototype, extension, override);
  };

  //============================================================================
  var extend = function (obj, extension, override) {
    var prop;
    if (override === false) {
      for (prop in extension)
        if (!(prop in obj))
          obj[prop] = extension[prop];
    } else {
      for (prop in extension)
        obj[prop] = extension[prop];
      if (extension.toString !== Object.prototype.toString)
        obj.toString = extension.toString;
    }
  };

})();

(function() {
var define, requireModule, require, requirejs;

(function() {
  var registry = {}, seen = {};

  define = function(name, deps, callback) {
    registry[name] = { deps: deps, callback: callback };
  };

  requirejs = require = requireModule = function(name) {
  requirejs._eak_seen = registry;

    if (seen[name]) { return seen[name]; }
    seen[name] = {};

    if (!registry[name]) {
      throw new Error("Could not find module " + name);
    }

    var mod = registry[name],
        deps = mod.deps,
        callback = mod.callback,
        reified = [],
        exports;

    for (var i=0, l=deps.length; i<l; i++) {
      if (deps[i] === 'exports') {
        reified.push(exports = {});
      } else {
        reified.push(requireModule(resolve(deps[i])));
      }
    }

    var value = callback.apply(this, reified);
    return seen[name] = exports || value;

    function resolve(child) {
      if (child.charAt(0) !== '.') { return child; }
      var parts = child.split("/");
      var parentBase = name.split("/").slice(0, -1);

      for (var i=0, l=parts.length; i<l; i++) {
        var part = parts[i];

        if (part === '..') { parentBase.pop(); }
        else if (part === '.') { continue; }
        else { parentBase.push(part); }
      }

      return parentBase.join("/");
    }
  };
})();

define("promise/all", 
  ["./utils","exports"],
  function(__dependency1__, __exports__) {
    "use strict";
    /* global toString */

    var isArray = __dependency1__.isArray;
    var isFunction = __dependency1__.isFunction;

    /**
      Returns a promise that is fulfilled when all the given promises have been
      fulfilled, or rejected if any of them become rejected. The return promise
      is fulfilled with an array that gives all the values in the order they were
      passed in the `promises` array argument.

      Example:

      ```javascript
      var promise1 = RSVP.resolve(1);
      var promise2 = RSVP.resolve(2);
      var promise3 = RSVP.resolve(3);
      var promises = [ promise1, promise2, promise3 ];

      RSVP.all(promises).then(function(array){
        // The array here would be [ 1, 2, 3 ];
      });
      ```

      If any of the `promises` given to `RSVP.all` are rejected, the first promise
      that is rejected will be given as an argument to the returned promises's
      rejection handler. For example:

      Example:

      ```javascript
      var promise1 = RSVP.resolve(1);
      var promise2 = RSVP.reject(new Error("2"));
      var promise3 = RSVP.reject(new Error("3"));
      var promises = [ promise1, promise2, promise3 ];

      RSVP.all(promises).then(function(array){
        // Code here never runs because there are rejected promises!
      }, function(error) {
        // error.message === "2"
      });
      ```

      @method all
      @for RSVP
      @param {Array} promises
      @param {String} label
      @return {Promise} promise that is fulfilled when all `promises` have been
      fulfilled, or rejected if any of them become rejected.
    */
    function all(promises) {
      /*jshint validthis:true */
      var Promise = this;

      if (!isArray(promises)) {
        throw new TypeError('You must pass an array to all.');
      }

      return new Promise(function(resolve, reject) {
        var results = [], remaining = promises.length,
        promise;

        if (remaining === 0) {
          resolve([]);
        }

        function resolver(index) {
          return function(value) {
            resolveAll(index, value);
          };
        }

        function resolveAll(index, value) {
          results[index] = value;
          if (--remaining === 0) {
            resolve(results);
          }
        }

        for (var i = 0; i < promises.length; i++) {
          promise = promises[i];

          if (promise && isFunction(promise.then)) {
            promise.then(resolver(i), reject);
          } else {
            resolveAll(i, promise);
          }
        }
      });
    }

    __exports__.all = all;
  });
define("promise/asap", 
  ["exports"],
  function(__exports__) {
    "use strict";
    var browserGlobal = (typeof window !== 'undefined') ? window : {};
    var BrowserMutationObserver = browserGlobal.MutationObserver || browserGlobal.WebKitMutationObserver;
    var local = (typeof global !== 'undefined') ? global : (this === undefined? window:this);

    // node
    function useNextTick() {
      return function() {
        process.nextTick(flush);
      };
    }

    function useMutationObserver() {
      var iterations = 0;
      var observer = new BrowserMutationObserver(flush);
      var node = document.createTextNode('');
      observer.observe(node, { characterData: true });

      return function() {
        node.data = (iterations = ++iterations % 2);
      };
    }

    function useSetTimeout() {
      return function() {
        local.setTimeout(flush, 1);
      };
    }

    var queue = [];
    function flush() {
      for (var i = 0; i < queue.length; i++) {
        var tuple = queue[i];
        var callback = tuple[0], arg = tuple[1];
        callback(arg);
      }
      queue = [];
    }

    var scheduleFlush;

    // Decide what async method to use to triggering processing of queued callbacks:
    if (typeof process !== 'undefined' && {}.toString.call(process) === '[object process]') {
      scheduleFlush = useNextTick();
    } else if (BrowserMutationObserver) {
      scheduleFlush = useMutationObserver();
    } else {
      scheduleFlush = useSetTimeout();
    }

    function asap(callback, arg) {
      var length = queue.push([callback, arg]);
      if (length === 1) {
        // If length is 1, that means that we need to schedule an async flush.
        // If additional callbacks are queued before the queue is flushed, they
        // will be processed by this flush that we are scheduling.
        scheduleFlush();
      }
    }

    __exports__.asap = asap;
  });
define("promise/config", 
  ["exports"],
  function(__exports__) {
    "use strict";
    var config = {
      instrument: false
    };

    function configure(name, value) {
      if (arguments.length === 2) {
        config[name] = value;
      } else {
        return config[name];
      }
    }

    __exports__.config = config;
    __exports__.configure = configure;
  });
define("promise/polyfill", 
  ["./promise","./utils","exports"],
  function(__dependency1__, __dependency2__, __exports__) {
    "use strict";
    /*global self*/
    var RSVPPromise = __dependency1__.Promise;
    var isFunction = __dependency2__.isFunction;

    function polyfill() {
      var local;

      if (typeof global !== 'undefined') {
        local = global;
      } else if (typeof window !== 'undefined' && window.document) {
        local = window;
      } else {
        local = self;
      }

      var es6PromiseSupport = 
        "Promise" in local &&
        // Some of these methods are missing from
        // Firefox/Chrome experimental implementations
        "resolve" in local.Promise &&
        "reject" in local.Promise &&
        "all" in local.Promise &&
        "race" in local.Promise &&
        // Older version of the spec had a resolver object
        // as the arg rather than a function
        (function() {
          var resolve;
          new local.Promise(function(r) { resolve = r; });
          return isFunction(resolve);
        }());

      if (!es6PromiseSupport) {
        local.Promise = RSVPPromise;
      }
    }

    __exports__.polyfill = polyfill;
  });
define("promise/promise", 
  ["./config","./utils","./all","./race","./resolve","./reject","./asap","exports"],
  function(__dependency1__, __dependency2__, __dependency3__, __dependency4__, __dependency5__, __dependency6__, __dependency7__, __exports__) {
    "use strict";
    var config = __dependency1__.config;
    var configure = __dependency1__.configure;
    var objectOrFunction = __dependency2__.objectOrFunction;
    var isFunction = __dependency2__.isFunction;
    var now = __dependency2__.now;
    var all = __dependency3__.all;
    var race = __dependency4__.race;
    var staticResolve = __dependency5__.resolve;
    var staticReject = __dependency6__.reject;
    var asap = __dependency7__.asap;

    var counter = 0;

    config.async = asap; // default async is asap;

    function Promise(resolver) {
      if (!isFunction(resolver)) {
        throw new TypeError('You must pass a resolver function as the first argument to the promise constructor');
      }

      if (!(this instanceof Promise)) {
        throw new TypeError("Failed to construct 'Promise': Please use the 'new' operator, this object constructor cannot be called as a function.");
      }

      this._subscribers = [];

      invokeResolver(resolver, this);
    }

    function invokeResolver(resolver, promise) {
      function resolvePromise(value) {
        resolve(promise, value);
      }

      function rejectPromise(reason) {
        reject(promise, reason);
      }

      try {
        resolver(resolvePromise, rejectPromise);
      } catch(e) {
        rejectPromise(e);
      }
    }

    function invokeCallback(settled, promise, callback, detail) {
      var hasCallback = isFunction(callback),
          value, error, succeeded, failed;

      if (hasCallback) {
        try {
          value = callback(detail);
          succeeded = true;
        } catch(e) {
          failed = true;
          error = e;
        }
      } else {
        value = detail;
        succeeded = true;
      }

      if (handleThenable(promise, value)) {
        return;
      } else if (hasCallback && succeeded) {
        resolve(promise, value);
      } else if (failed) {
        reject(promise, error);
      } else if (settled === FULFILLED) {
        resolve(promise, value);
      } else if (settled === REJECTED) {
        reject(promise, value);
      }
    }

    var PENDING   = void 0;
    var SEALED    = 0;
    var FULFILLED = 1;
    var REJECTED  = 2;

    function subscribe(parent, child, onFulfillment, onRejection) {
      var subscribers = parent._subscribers;
      var length = subscribers.length;

      subscribers[length] = child;
      subscribers[length + FULFILLED] = onFulfillment;
      subscribers[length + REJECTED]  = onRejection;
    }

    function publish(promise, settled) {
      var child, callback, subscribers = promise._subscribers, detail = promise._detail;

      for (var i = 0; i < subscribers.length; i += 3) {
        child = subscribers[i];
        callback = subscribers[i + settled];

        invokeCallback(settled, child, callback, detail);
      }

      promise._subscribers = null;
    }

    Promise.prototype = {
      constructor: Promise,

      _state: undefined,
      _detail: undefined,
      _subscribers: undefined,

      then: function(onFulfillment, onRejection) {
        var promise = this;

        var thenPromise = new this.constructor(function() {});

        if (this._state) {
          var callbacks = arguments;
          config.async(function invokePromiseCallback() {
            invokeCallback(promise._state, thenPromise, callbacks[promise._state - 1], promise._detail);
          });
        } else {
          subscribe(this, thenPromise, onFulfillment, onRejection);
        }

        return thenPromise;
      },

      'catch': function(onRejection) {
        return this.then(null, onRejection);
      }
    };

    Promise.all = all;
    Promise.race = race;
    Promise.resolve = staticResolve;
    Promise.reject = staticReject;

    function handleThenable(promise, value) {
      var then = null,
      resolved;

      try {
        if (promise === value) {
          throw new TypeError("A promises callback cannot return that same promise.");
        }

        if (objectOrFunction(value)) {
          then = value.then;

          if (isFunction(then)) {
            then.call(value, function(val) {
              if (resolved) { return true; }
              resolved = true;

              if (value !== val) {
                resolve(promise, val);
              } else {
                fulfill(promise, val);
              }
            }, function(val) {
              if (resolved) { return true; }
              resolved = true;

              reject(promise, val);
            });

            return true;
          }
        }
      } catch (error) {
        if (resolved) { return true; }
        reject(promise, error);
        return true;
      }

      return false;
    }

    function resolve(promise, value) {
      if (promise === value) {
        fulfill(promise, value);
      } else if (!handleThenable(promise, value)) {
        fulfill(promise, value);
      }
    }

    function fulfill(promise, value) {
      if (promise._state !== PENDING) { return; }
      promise._state = SEALED;
      promise._detail = value;

      config.async(publishFulfillment, promise);
    }

    function reject(promise, reason) {
      if (promise._state !== PENDING) { return; }
      promise._state = SEALED;
      promise._detail = reason;

      config.async(publishRejection, promise);
    }

    function publishFulfillment(promise) {
      publish(promise, promise._state = FULFILLED);
    }

    function publishRejection(promise) {
      publish(promise, promise._state = REJECTED);
    }

    __exports__.Promise = Promise;
  });
define("promise/race", 
  ["./utils","exports"],
  function(__dependency1__, __exports__) {
    "use strict";
    /* global toString */
    var isArray = __dependency1__.isArray;

    /**
      `RSVP.race` allows you to watch a series of promises and act as soon as the
      first promise given to the `promises` argument fulfills or rejects.

      Example:

      ```javascript
      var promise1 = new RSVP.Promise(function(resolve, reject){
        setTimeout(function(){
          resolve("promise 1");
        }, 200);
      });

      var promise2 = new RSVP.Promise(function(resolve, reject){
        setTimeout(function(){
          resolve("promise 2");
        }, 100);
      });

      RSVP.race([promise1, promise2]).then(function(result){
        // result === "promise 2" because it was resolved before promise1
        // was resolved.
      });
      ```

      `RSVP.race` is deterministic in that only the state of the first completed
      promise matters. For example, even if other promises given to the `promises`
      array argument are resolved, but the first completed promise has become
      rejected before the other promises became fulfilled, the returned promise
      will become rejected:

      ```javascript
      var promise1 = new RSVP.Promise(function(resolve, reject){
        setTimeout(function(){
          resolve("promise 1");
        }, 200);
      });

      var promise2 = new RSVP.Promise(function(resolve, reject){
        setTimeout(function(){
          reject(new Error("promise 2"));
        }, 100);
      });

      RSVP.race([promise1, promise2]).then(function(result){
        // Code here never runs because there are rejected promises!
      }, function(reason){
        // reason.message === "promise2" because promise 2 became rejected before
        // promise 1 became fulfilled
      });
      ```

      @method race
      @for RSVP
      @param {Array} promises array of promises to observe
      @param {String} label optional string for describing the promise returned.
      Useful for tooling.
      @return {Promise} a promise that becomes fulfilled with the value the first
      completed promises is resolved with if the first completed promise was
      fulfilled, or rejected with the reason that the first completed promise
      was rejected with.
    */
    function race(promises) {
      /*jshint validthis:true */
      var Promise = this;

      if (!isArray(promises)) {
        throw new TypeError('You must pass an array to race.');
      }
      return new Promise(function(resolve, reject) {
        var results = [], promise;

        for (var i = 0; i < promises.length; i++) {
          promise = promises[i];

          if (promise && typeof promise.then === 'function') {
            promise.then(resolve, reject);
          } else {
            resolve(promise);
          }
        }
      });
    }

    __exports__.race = race;
  });
define("promise/reject", 
  ["exports"],
  function(__exports__) {
    "use strict";
    /**
      `RSVP.reject` returns a promise that will become rejected with the passed
      `reason`. `RSVP.reject` is essentially shorthand for the following:

      ```javascript
      var promise = new RSVP.Promise(function(resolve, reject){
        reject(new Error('WHOOPS'));
      });

      promise.then(function(value){
        // Code here doesn't run because the promise is rejected!
      }, function(reason){
        // reason.message === 'WHOOPS'
      });
      ```

      Instead of writing the above, your code now simply becomes the following:

      ```javascript
      var promise = RSVP.reject(new Error('WHOOPS'));

      promise.then(function(value){
        // Code here doesn't run because the promise is rejected!
      }, function(reason){
        // reason.message === 'WHOOPS'
      });
      ```

      @method reject
      @for RSVP
      @param {Any} reason value that the returned promise will be rejected with.
      @param {String} label optional string for identifying the returned promise.
      Useful for tooling.
      @return {Promise} a promise that will become rejected with the given
      `reason`.
    */
    function reject(reason) {
      /*jshint validthis:true */
      var Promise = this;

      return new Promise(function (resolve, reject) {
        reject(reason);
      });
    }

    __exports__.reject = reject;
  });
define("promise/resolve", 
  ["exports"],
  function(__exports__) {
    "use strict";
    function resolve(value) {
      /*jshint validthis:true */
      if (value && typeof value === 'object' && value.constructor === this) {
        return value;
      }

      var Promise = this;

      return new Promise(function(resolve) {
        resolve(value);
      });
    }

    __exports__.resolve = resolve;
  });
define("promise/utils", 
  ["exports"],
  function(__exports__) {
    "use strict";
    function objectOrFunction(x) {
      return isFunction(x) || (typeof x === "object" && x !== null);
    }

    function isFunction(x) {
      return typeof x === "function";
    }

    function isArray(x) {
      return Object.prototype.toString.call(x) === "[object Array]";
    }

    // Date.now is not available in browsers < IE9
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/now#Compatibility
    var now = Date.now || function() { return new Date().getTime(); };


    __exports__.objectOrFunction = objectOrFunction;
    __exports__.isFunction = isFunction;
    __exports__.isArray = isArray;
    __exports__.now = now;
  });
requireModule('promise/polyfill').polyfill();
}());

/*global define:false, require:false, exports:false, module:false, signals:false */

/** @license
 * JS Signals <http://millermedeiros.github.com/js-signals/>
 * Released under the MIT license
 * Author: Miller Medeiros
 * Version: 1.0.0 - Build: 268 (2012/11/29 05:48 PM)
 */

(function(global){

    // SignalBinding -------------------------------------------------
    //================================================================

    /**
     * Object that represents a binding between a Signal and a listener function.
     * <br />- <strong>This is an internal constructor and shouldn't be called by regular users.</strong>
     * <br />- inspired by Joa Ebert AS3 SignalBinding and Robert Penner's Slot classes.
     * @author Miller Medeiros
     * @constructor
     * @internal
     * @name SignalBinding
     * @param {Signal} signal Reference to Signal object that listener is currently bound to.
     * @param {Function} listener Handler function bound to the signal.
     * @param {boolean} isOnce If binding should be executed just once.
     * @param {Object} [listenerContext] Context on which listener will be executed (object that should represent the `this` variable inside listener function).
     * @param {Number} [priority] The priority level of the event listener. (default = 0).
     */
    function SignalBinding(signal, listener, isOnce, listenerContext, priority) {

        /**
         * Handler function bound to the signal.
         * @type Function
         * @private
         */
        this._listener = listener;

        /**
         * If binding should be executed just once.
         * @type boolean
         * @private
         */
        this._isOnce = isOnce;

        /**
         * Context on which listener will be executed (object that should represent the `this` variable inside listener function).
         * @memberOf SignalBinding.prototype
         * @name context
         * @type Object|undefined|null
         */
        this.context = listenerContext;

        /**
         * Reference to Signal object that listener is currently bound to.
         * @type Signal
         * @private
         */
        this._signal = signal;

        /**
         * Listener priority
         * @type Number
         * @private
         */
        this._priority = priority || 0;
    }

    SignalBinding.prototype = {

        /**
         * If binding is active and should be executed.
         * @type boolean
         */
        active : true,

        /**
         * Default parameters passed to listener during `Signal.dispatch` and `SignalBinding.execute`. (curried parameters)
         * @type Array|null
         */
        params : null,

        /**
         * Call listener passing arbitrary parameters.
         * <p>If binding was added using `Signal.addOnce()` it will be automatically removed from signal dispatch queue, this method is used internally for the signal dispatch.</p>
         * @param {Array} [paramsArr] Array of parameters that should be passed to the listener
         * @return {*} Value returned by the listener.
         */
        execute : function (paramsArr) {
            var handlerReturn, params;
            if (this.active && !!this._listener) {
                params = this.params? this.params.concat(paramsArr) : paramsArr;
                handlerReturn = this._listener.apply(this.context, params);
                if (this._isOnce) {
                    this.detach();
                }
            }
            return handlerReturn;
        },

        /**
         * Detach binding from signal.
         * - alias to: mySignal.remove(myBinding.getListener());
         * @return {Function|null} Handler function bound to the signal or `null` if binding was previously detached.
         */
        detach : function () {
            return this.isBound()? this._signal.remove(this._listener, this.context) : null;
        },

        /**
         * @return {Boolean} `true` if binding is still bound to the signal and have a listener.
         */
        isBound : function () {
            return (!!this._signal && !!this._listener);
        },

        /**
         * @return {boolean} If SignalBinding will only be executed once.
         */
        isOnce : function () {
            return this._isOnce;
        },

        /**
         * @return {Function} Handler function bound to the signal.
         */
        getListener : function () {
            return this._listener;
        },

        /**
         * @return {Signal} Signal that listener is currently bound to.
         */
        getSignal : function () {
            return this._signal;
        },

        /**
         * Delete instance properties
         * @private
         */
        _destroy : function () {
            delete this._signal;
            delete this._listener;
            delete this.context;
        },

        /**
         * @return {string} String representation of the object.
         */
        toString : function () {
            return '[SignalBinding isOnce:' + this._isOnce +', isBound:'+ this.isBound() +', active:' + this.active + ']';
        }

    };


/*global SignalBinding:false*/

    // Signal --------------------------------------------------------
    //================================================================

    function validateListener(listener, fnName) {
        if (typeof listener !== 'function') {
            throw new Error( 'listener is a required param of {fn}() and should be a Function.'.replace('{fn}', fnName) );
        }
    }

    /**
     * Custom event broadcaster
     * <br />- inspired by Robert Penner's AS3 Signals.
     * @name Signal
     * @author Miller Medeiros
     * @constructor
     */
    function Signal() {
        /**
         * @type Array.<SignalBinding>
         * @private
         */
        this._bindings = [];
        this._prevParams = null;

        // enforce dispatch to aways work on same context (#47)
        var self = this;
        this.dispatch = function(){
            Signal.prototype.dispatch.apply(self, arguments);
        };
    }

    Signal.prototype = {

        /**
         * Signals Version Number
         * @type String
         * @const
         */
        VERSION : '1.0.0',

        /**
         * If Signal should keep record of previously dispatched parameters and
         * automatically execute listener during `add()`/`addOnce()` if Signal was
         * already dispatched before.
         * @type boolean
         */
        memorize : false,

        /**
         * @type boolean
         * @private
         */
        _shouldPropagate : true,

        /**
         * If Signal is active and should broadcast events.
         * <p><strong>IMPORTANT:</strong> Setting this property during a dispatch will only affect the next dispatch, if you want to stop the propagation of a signal use `halt()` instead.</p>
         * @type boolean
         */
        active : true,

        /**
         * @param {Function} listener
         * @param {boolean} isOnce
         * @param {Object} [listenerContext]
         * @param {Number} [priority]
         * @return {SignalBinding}
         * @private
         */
        _registerListener : function (listener, isOnce, listenerContext, priority) {

            var prevIndex = this._indexOfListener(listener, listenerContext),
                binding;

            if (prevIndex !== -1) {
                binding = this._bindings[prevIndex];
                if (binding.isOnce() !== isOnce) {
                    throw new Error('You cannot add'+ (isOnce? '' : 'Once') +'() then add'+ (!isOnce? '' : 'Once') +'() the same listener without removing the relationship first.');
                }
            } else {
                binding = new SignalBinding(this, listener, isOnce, listenerContext, priority);
                this._addBinding(binding);
            }

            if(this.memorize && this._prevParams){
                binding.execute(this._prevParams);
            }

            return binding;
        },

        /**
         * @param {SignalBinding} binding
         * @private
         */
        _addBinding : function (binding) {
            //simplified insertion sort
            var n = this._bindings.length;
            do { --n; } while (this._bindings[n] && binding._priority <= this._bindings[n]._priority);
            this._bindings.splice(n + 1, 0, binding);
        },

        /**
         * @param {Function} listener
         * @return {number}
         * @private
         */
        _indexOfListener : function (listener, context) {
            var n = this._bindings.length,
                cur;
            while (n--) {
                cur = this._bindings[n];
                if (cur._listener === listener && cur.context === context) {
                    return n;
                }
            }
            return -1;
        },

        /**
         * Check if listener was attached to Signal.
         * @param {Function} listener
         * @param {Object} [context]
         * @return {boolean} if Signal has the specified listener.
         */
        has : function (listener, context) {
            return this._indexOfListener(listener, context) !== -1;
        },

        /**
         * Add a listener to the signal.
         * @param {Function} listener Signal handler function.
         * @param {Object} [listenerContext] Context on which listener will be executed (object that should represent the `this` variable inside listener function).
         * @param {Number} [priority] The priority level of the event listener. Listeners with higher priority will be executed before listeners with lower priority. Listeners with same priority level will be executed at the same order as they were added. (default = 0)
         * @return {SignalBinding} An Object representing the binding between the Signal and listener.
         */
        add : function (listener, listenerContext, priority) {
            validateListener(listener, 'add');
            return this._registerListener(listener, false, listenerContext, priority);
        },

        /**
         * Add listener to the signal that should be removed after first execution (will be executed only once).
         * @param {Function} listener Signal handler function.
         * @param {Object} [listenerContext] Context on which listener will be executed (object that should represent the `this` variable inside listener function).
         * @param {Number} [priority] The priority level of the event listener. Listeners with higher priority will be executed before listeners with lower priority. Listeners with same priority level will be executed at the same order as they were added. (default = 0)
         * @return {SignalBinding} An Object representing the binding between the Signal and listener.
         */
        addOnce : function (listener, listenerContext, priority) {
            validateListener(listener, 'addOnce');
            return this._registerListener(listener, true, listenerContext, priority);
        },

        /**
         * Remove a single listener from the dispatch queue.
         * @param {Function} listener Handler function that should be removed.
         * @param {Object} [context] Execution context (since you can add the same handler multiple times if executing in a different context).
         * @return {Function} Listener handler function.
         */
        remove : function (listener, context) {
            validateListener(listener, 'remove');

            var i = this._indexOfListener(listener, context);
            if (i !== -1) {
                this._bindings[i]._destroy(); //no reason to a SignalBinding exist if it isn't attached to a signal
                this._bindings.splice(i, 1);
            }
            return listener;
        },

        /**
         * Remove all listeners from the Signal.
         */
        removeAll : function () {
            var n = this._bindings.length;
            while (n--) {
                this._bindings[n]._destroy();
            }
            this._bindings.length = 0;
        },

        /**
         * @return {number} Number of listeners attached to the Signal.
         */
        getNumListeners : function () {
            return this._bindings.length;
        },

        /**
         * Stop propagation of the event, blocking the dispatch to next listeners on the queue.
         * <p><strong>IMPORTANT:</strong> should be called only during signal dispatch, calling it before/after dispatch won't affect signal broadcast.</p>
         * @see Signal.prototype.disable
         */
        halt : function () {
            this._shouldPropagate = false;
        },

        /**
         * Dispatch/Broadcast Signal to all listeners added to the queue.
         * @param {...*} [params] Parameters that should be passed to each handler.
         */
        dispatch : function (params) {
            if (! this.active) {
                return;
            }

            var paramsArr = Array.prototype.slice.call(arguments),
                n = this._bindings.length,
                bindings;

            if (this.memorize) {
                this._prevParams = paramsArr;
            }

            if (! n) {
                //should come after memorize
                return;
            }

            bindings = this._bindings.slice(); //clone array in case add/remove items during dispatch
            this._shouldPropagate = true; //in case `halt` was called before dispatch or during the previous dispatch.

            //execute all callbacks until end of the list or until a callback returns `false` or stops propagation
            //reverse loop since listeners with higher priority will be added at the end of the list
            do { n--; } while (bindings[n] && this._shouldPropagate && bindings[n].execute(paramsArr) !== false);
        },

        /**
         * Forget memorized arguments.
         * @see Signal.memorize
         */
        forget : function(){
            this._prevParams = null;
        },

        /**
         * Remove all bindings from signal and destroy any reference to external objects (destroy Signal object).
         * <p><strong>IMPORTANT:</strong> calling any method on the signal instance after calling dispose will throw errors.</p>
         */
        dispose : function () {
            this.removeAll();
            delete this._bindings;
            delete this._prevParams;
        },

        /**
         * @return {string} String representation of the object.
         */
        toString : function () {
            return '[Signal active:'+ this.active +' numListeners:'+ this.getNumListeners() +']';
        }

    };


    // Namespace -----------------------------------------------------
    //================================================================

    /**
     * Signals namespace
     * @namespace
     * @name signals
     */
    var signals = Signal;

    /**
     * Custom event broadcaster
     * @see Signal
     */
    // alias for backwards compatibility (see #gh-44)
    signals.Signal = Signal;



    //exports to multiple environments
    if(typeof define === 'function' && define.amd){ //AMD
        define(function () { return signals; });
    } else if (typeof module !== 'undefined' && module.exports){ //node
        module.exports = signals;
    } else { //browser
        //use string because of Google closure compiler ADVANCED_MODE
        /*jslint sub:true */
        global['signals'] = signals;
    }

}(this));

// Based on json-stable-stringify, but simpler.

function CycleError() {
  this.name = "CycleError";
  this.message = "Cycles are not allowed";
}
CycleError.prototype = new Error();
CycleError.constructor = CycleError;

var stableStringify = (function() {
  var isArray = Array.isArray || function (x) {
      return {}.toString.call(x) === '[object Array]';
  };

  var objectKeys = Object.keys || function (obj) {
      var has = Object.prototype.hasOwnProperty || function () { return true; };
      var keys = [];
      for (var key in obj) {
          if (has.call(obj, key))
            keys.push(key);
      }
      return keys;
  };

  return function stringify(node) {
    var i;

    if (typeof node !== "object" || node === null) {
      return JSON.stringify(node);
    } else if (isArray(node)) {
      if (node.__cycle__) {
        throw new CycleError();
      }

      node.__cycle__ = true;
      try {
        var children = [];
        for (i = 0; i < node.length; i++) {
          children.push(stringify(node[i]));
        }
        return "[" + children.join(",") + "]";
      } finally {
        delete node.__cycle__;
      }
    } else {
      if (node.__cycle__) {
        throw new CycleError();
      }

      node.__cycle__ = true;
      try {
        var keys = objectKeys(node);
        keys.sort();

        var items = [];
        for (i = 0; i < keys.length; i++) {
          if (keys[i] == "__cycle__") {
            continue;
          }
          var keyStr = JSON.stringify(keys[i]);
          var valStr = stringify(node[keys[i]]);
          items.push(keyStr + ":" + valStr);
        }
        return "{" + items.join(",") + "}";
      } finally {
        delete node.__cycle__;
      }
    }
  };
})();

var Snorky = (function(Class) {
  "use strict";

  // Minimal lodash-style implementation
  var _ = {
    each: function(collection, callback, thisArg) {
      for (var key in collection) {
        if (callback.call(thisArg, collection[key], key, collection) === false) {
          break;
        }
      }
    },
    assign: function(object, source) {
      for (var key in source) {
        object[key] = source[key];
      }
      return object;
    },
    defaults: function(object, source) {
      object = object || {};
      for (var key in source) {
        if (!(key in object)) {
          object[key] = source[key];
        }
      }
      return object;
    },
    map: function(array, callback, thisArg) {
      var ret = [];
      _.each(array, function(val) {
        ret.push(callback.call(thisArg, val));
      });
      return ret;
    },
    keys: function(obj) {
      var keys = [];
      for (var k in obj) {
        keys.push(k);
      }
      return keys;
    },
    findIndex: function(array, callback, thisArg) {
      var ret;
      _.each(array, function(value, index) {
        if (callback.call(thisArg, value)) {
          ret = index;
          return false;
        }
      });
      return ret;
    },
    find: function(array, callback, thisArg) {
      var index = _.findIndex(array, callback, thisArg);
      if (index !== undefined) {
        return array[index];
      }
    },
    remove: function(array, callback, thisArg) {
      var removedItems = [];

      for (var i = 0; i < array.length; i++) {
        var value = array[i];
        if (callback.call(thisArg, value)) {
          removedItems.push(value);
          array.splice(i, 1);
          i--;
        }
      }

      return removedItems;
    },
    isArray: function(thing) {
      return Object.prototype.toString.call(thing) === "[object Array]";
    },
    indexOf: function(haystack, needle) {
      for (var i = 0; i < haystack.length; i++) {
        if (haystack[i] === needle) {
          return i;
        }
      }
      return -1;
    },
    in: function(haystack, needle) {
      // TODO: Rename to `contains`
      if (_.isArray(haystack)) {
        return _.indexOf(haystack, needle) != -1;
      } else {
        return (needle in haystack);
      }
    },
    subset: function(object, allowedKeys, errorFn) {
      errorFn = errorFn || function() {};
      _.each(object, function(value, key) {
        if (!_.in(allowedKeys, key)) {
          errorFn(key, value);
        }
      });
    },
    replace: function(array, newValue, callback, thisArg) {
      // Replaces elements that make callback() return true with `newValue`.
      var ret;
      _.each(array, function(value, index) {
        if (callback.call(thisArg, value)) {
          array[index] = newValue;
          ret = value;
        }
      });
      return ret;
    },
    field: function(fieldName, object) {
      // Returns a function that compares that takes an object as argument and
      // compares it to `object` on the field `fieldName`.
      return function(otherObject) {
        return otherObject[fieldName] == object[fieldName];
      };
    },
    replaceOnField: function(fieldName, array, newValue) {
      return _.replace(array, newValue, _.field(fieldName, newValue));
    },
    removeOnField: function(fieldName, array, needle) {
      _.remove(array, _.field(fieldName, needle));
    },
    isEqualRight: function(bigObject, smallObject) {
      for (var key in smallObject) {
        if (bigObject[key] !== smallObject[key]) {
          return false;
        }
      }
      return true;
    }
  };

  var Snorky = new Class({
    constructor: function(socketClass, address, services, options) {
      options = options || {};
      this.address = address;
      this.socketClass = socketClass;
      this.debug = (options.debug !== undefined ? options.debug : false);
      this.services = {};

      for (var serviceName in services) {
        var ServiceClass = services[serviceName];
        this.services[serviceName] = new ServiceClass(serviceName, this);
      }

      this._socket = null;
      this._queuedMessages = [];
      this.isConnected = false;
      this.isConnecting = false;

      this.connected = new Snorky.Signal();
      this.disconnected = new Snorky.Signal();

      this.connect();
    },

    logDebug: function() {
      // Do not use console.log when console is undefined (e.g. Internet
      // Explorer)
      if (this.debug && console && console.log)
      {
        // Use console.debug() falling back to console.log() if unavailable
        var debug = console.debug || console.log;

        if (debug.apply) {
          debug.apply(console, arguments);
        } else {
          // Some versions of IE do not have apply
          var a = arguments;
          debug(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9],
                a[10], a[11], a[12]);
        }
      }
    },

    connect: function() {
      var self = this;

      this.isConnecting = true;

      this._socket = new this.socketClass(this.address);
      this._socket.onopen = function() {
        self._onSocketOpen();
      };
      this._socket.onmessage = function(e) {
        self._onSocketMessage(e);
      };
      this._socket.onclose = function() {
        self._onSocketClose();
      };
    },

    disconnect: function() {
      this._socket.close();

      // Set as disconnected immediately
      this.isConnected = false;
    },

    _onSocketOpen: function() {
      this.logDebug("Connected to Snorky server.");

      this.isConnected = true;
      this.isConnecting = false;

      this.connected.dispatch();

      _.each(this._queuedMessages, function(rawMessage) {
        this._socket.send(rawMessage);
      }, this);
      this._queuedMessages = [];
    },

    _onSocketMessage: function(event) {
      var rawMessage = event.data;
      var packet = JSON.parse(rawMessage);
      var service = packet.service;
      if (service in this.services) {
        // TODO Refactor message to content?
        this.services[service].packetReceived.dispatch(packet.message);
      }
    },

    _onSocketClose: function() {
      this.logDebug("Snorky disconnected");

      this.isConnected = false;
      this.isConnecting = false;

      this.disconnected.dispatch();
      this._socket = null;
    },

    _sendServiceMessage: function(serviceName, message) {
      var rawMessage = JSON.stringify({
        "service": serviceName,
        "message": message
      });

      if (this.isConnected) {
        this._socket.send(rawMessage);
      } else {
        this._queuedMessages.push(rawMessage);
      }
    }

  });

  // Export Class and _
  Snorky.Class = Class;
  Snorky._ = _;

  // Export Signal class and allow replacing it
  if (typeof signals !== "undefined") {
    Snorky.Signal = signals.Signal;
  }

  // Snorky will use ES6 promises by default, but it allows switching
  Snorky.Promise = Promise;

  return Snorky;

})(my.Class);

(function() {
  "use strict";

  var Class = Snorky.Class;
  var _ = Snorky._;

  Snorky.Service = new Class({
    constructor: function(name, snorky) {
      if (!name instanceof String|| !snorky) {
        throw Error("Bad arguments for service constructor");
      }
      this.name = name;
      this.snorky = snorky;

      this.packetReceived = new Snorky.Signal();

      this.init();
    },

    init: function() {
      // noop
    },

    sendMessage: function(message) {
      this.snorky._sendServiceMessage(this.name, message);
    }
  });

  Snorky.RPCService = new Class(Snorky.Service, {
    init: function() {
      this.nextCallId = 0;
      this.calls = {}; // callId -> Promise

      this.packetReceived.add(this.onPacket, this);
      this.notificationReceived = new Snorky.Signal();
    },

    rpcCall: function(command, params) {
      var self = this;
      return new Snorky.Promise(function(resolve, reject) {
        var callId = self.nextCallId++;
        self.calls[callId] = { "resolve": resolve, "reject": reject };

        self.sendMessage({
          "command": command,
          "params": params,
          "callId": callId
        });
      });
    },

    onPacket: function(message) {
      if (!("type" in message)) {
        console.error('Non-RPC message received from service "%s"',
                      this.name);
        return;
      }

      if (message.type == "response" || message.type == "error") {
        // Check for a known callId
        if (!(message.callId in this.calls)) {
          console.error(
            'Response for unknown call with id "%s" from service "%s"',
            message.callId, this.name);
          return;
        }
      }

      if (message.type == "response") {
        this.calls[message.callId].resolve(message.data);
      } else if (message.type == "error") {
        this.calls[message.callId].reject(Error(message.message));
      } else {
        this.notificationReceived.dispatch(message);
      }
    },

    STATIC: {
      addRPCMethods: function(methods) {
        // Convenience function to add RPC methods to the class

        var cls = this;
        _.each(methods, function(method) {
          // Prevent the user from breaking internal existing methods
          if (method in cls.prototype) {
            throw Error('Method "' + method + '" already exists in the ' +
                        'class. Refusing to overwrite it.');
          }

          cls.prototype[method] = function(params) {
            return this.rpcCall(method, params || {});
          };
        });
      }
    }
  });

})();

(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.Messaging = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);

      this.notificationReceived.add(this.onNotification, this);
      this.messageReceived = new Snorky.Signal();
    },

    onNotification: function(message) {
      if (message.type == "message") {
        this.messageReceived.dispatch(message);
      } else {
        console.error("Unknown message type in messaging service: " +
                      message.type);
      }
    }
  });
  Snorky.Messaging.addRPCMethods([
    "registerParticipant",
    "unregisterParticipant",
    "listParticipants",
    "send"
  ]);

})();

(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.PubSub = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);

      this.notificationReceived.add(this.onNotification, this);
      this.messagePublished = new Snorky.Signal();
    },

    onNotification: function(message) {
      if (message.type == "message") {
        this.messagePublished.dispatch(message);
      } else {
        console.error("Unknown message type in messaging service: " +
                      message.type);
      }
    }
  });
  Snorky.PubSub.addRPCMethods([
    "publish",
    "subscribe",
    "unsubscribe"
  ]);

})();

(function() {
  "use strict";

  var Class = Snorky.Class;
  var _ = Snorky._;

  Snorky.DataSync = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);
      this.notificationReceived.add(this.onNotification, this);
      this.deltaReceived = new Snorky.Signal();
    },

    onNotification: function(message) {
      if (message.type == "delta") {
        this.deltaReceived.dispatch(message.delta);
      } else {
        console.error("Unknown message type in DataSync service: " +
                      message.type);
      }
    }
  });
  Snorky.DataSync.addRPCMethods([
    "acquireSubscription",
    "cancelSubscription"
  ]);


  var CollectionDeltaProcessor = Snorky.DataSync.CollectionDeltaProcessor =
  new Class({
    constructor: function(collections, options) {
      this.collections = collections || {};
      options = options || {};
      if (options.itemsAreEqual) {
        this.itemsAreEqual = options.itemsAreEqual;
      }
    },

    itemsAreEqual: function(item, other, delta) {
      return item.id == other.id;
    },

    processDelta: function(delta) {
      var collection;
      var iter, item;

      if (!(delta.model in this.collections)) {
        if (console && console.error) {
          console.error("Received delta for unregistered model: " +
                        delta.model);
        }
        return;
      }

      // There are two ways to register collections and models.
      //
      // Simple way:
      // collections = { "Player": new ArrayCollection(...) }
      //
      // Tagged way (in order to have several views of the same model):
      // collections = { "Player": {
      //   "redPlayers": new ArrayCollection(...),
      //   "bluePlayers": new ArrayCollection(...)
      // } }
      if (this.collections[delta.model] instanceof
          Snorky.DataSync.Collection)
      {
        collection = this.collections[delta.model];
      } else {
        // Expect a dictionary of tag -> collection
        if (!(delta.tag in this.collections[delta.model])) {
          if (console && console.error) {
            console.error("Received delta with unregistered tag: " +
                          delta.tag + " (model: " + delta.model + ")");
          }
          return;
        }
        collection = this.collections[delta.model][delta.tag];
      }

      // Apply the delta on the collection
      if (delta.type == "insert") {
        collection.insert(delta.data);
      } else if (delta.type == "update") {
        iter = collection.getIterator();
        while (iter.hasNext()) {
          item = iter.next();
          if (this.itemsAreEqual(item, delta.oldData)) {
            iter.update(delta.newData);
            break;
          }
        }
      } else if (delta.type == "delete") {
        iter = collection.getIterator();
        while (iter.hasNext()) {
          item = iter.next();
          if (this.itemsAreEqual(item, delta.data)) {
            iter.remove();
            break;
          }
        }
      } else {
        if (console && console.error) {
          console.error("Received delta of strange type: " + delta.type);
        }
      }
    }
  });

  /* Data container and iterator for array */

  var Collection = Snorky.DataSync.Collection = new Class({});

  var ArrayIterator = Snorky.DataSync.ArrayIterator =
  new Class({
    constructor: function(array, options) {
      this.array = array;
      this.options = options;
    },

    array: null,
    index: -1,
    deleted: false,
    options: {},

    hasNext: function() {
      var lastIndex = this.array.length - 1;
      return (this.index < lastIndex);
    },

    next: function() {
      if (!this.hasNext()) {
        throw new Error("Busted iterator");
      }
      this.deleted = false;
      return this.array[++this.index];
    },

    checkSafe: function() {
      if (this.deleted) {
        throw new Error("Iterator pointing to a deleted item! (call next())");
      } else if (this.index == -1) {
        throw new Error("Iterator not pointing to an item! (call next())");
      }
    },

    remove: function() {
      this.checkSafe();

      this.array.splice(this.index--, 1);
      this.deleted = true;
    },

    update: function(newVal) {
      this.checkSafe();

      this.array[this.index] = this.options.transformItem(newVal);
    }
  });


  var ArrayCollection = Snorky.DataSync.ArrayCollection =
  new Class(Collection, {
    constructor: function(array, options) {
      this.array = array;
      this.options = _.defaults(options, {
        transformItem: function(item) {
          return item;
        }
      });
    },

    array: null,
    options: {},

    insert: function(val) {
      var transformed = this.options.transformItem(val);
      this.array.push(transformed);
    },

    getIterator: function() {
      return new ArrayIterator(this.array, this.options);
    }
  });


  /* Virtual single-item collection and iterator */

  var SingleItemIterator = Snorky.DataSync.SingleItemIterator =
  new Class({
    constructor: function(collection) {
      this.fetched = false;
      this.collection = collection;
    },

    fetched: false,
    collection: null,

    hasNext: function() {
      return !this.fetched;
    },

    next: function() {
      if (this.fetched) {
        throw new Error("Busted iterator");
      }
      this.fetched = true;
      return this.collection.readHandler();
    },

    remove: function() {
      if (!this.fetched) {
        throw new Error("Iterator not pointing to an item! (call next())");
      }
      this.collection.removeHandler();
    },

    update: function(newVal) {
      if (!this.fetched) {
        throw new Error("Iterator not pointing to an item! (call next())");
      }
      this.collection.updateHandler(newVal);
    }
  });

  var SingleItemCollection = Snorky.DataSync.SingleItemCollection =
  new Class(Collection, {
    constructor: function(readHandler, updateHandler, removeHandler) {
      this.readHandler = readHandler;
      this.updateHandler = updateHandler;
      this.removeHandler = removeHandler || function () {};
    },

    item: null,

    insert: function(val) {
      if (console && console.error) {
        console.error("Received insert() request in SingleItemCollection");
      }
    },

    getIterator: function() {
      return new SingleItemIterator(this);
    }
  });

})();

(function() {
  "use strict";

  var Class = Snorky.Class;

  Snorky.Chat = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);

      this.notificationReceived.add(this.onNotification, this);

      this.messageReceived = new Snorky.Signal();
      this.presenceReceived = new Snorky.Signal();
      this.readReceived = new Snorky.Signal();
    },

    onNotification: function(message) {
      if (message.type == "message") {
        this.messageReceived.dispatch(message);
      } else if (message.type == "presence") {
        this.presenceReceived.dispatch(message);
      } else if (message.type == "read") {
        this.readReceived.dispatch(message);
      } else {
        console.error("Unknown message type in messaging service: " +
                      message.type);
      }
    }
  });
  Snorky.Chat.addRPCMethods([
    "join",
    "leave",
    "send",
    "read"
  ]);

})();


(function() {
  "use strict";

  var Class = Snorky.Class;
  var _ = Snorky._;

  var Cursor = new Class({});

  var ForeignCursor = new Class(Cursor, {
    constructor: function(data) {
      _.assign(this, data);
    },

    isMine: false
  });

  var OwnCursor = new Class(Cursor, {
    constructor: function(document, data) {
      this.document = document;
      this.removed = false;
      _.assign(this, data);

      this.pendingPromiseCount = 1; // The create request is pending still
    },

    isMine: true,

    update: function(newData) {
      var self = this;
      var service = this.document.service;
      self.pendingPromiseCount += 1;

      _.subset(newData, ["position", "status"], function(key) {
        throw new Error("Can't update '" + key + "' of cursor.");
      });

      // Optimization: skip rpcCall if old data and new data are equal
      if (_.isEqualRight(this, newData)) {
        return new Promise(function(success) { success(); });
      } else {
        _.assign(this, newData);

        return service.rpcCall("updateCursor", {
          privateHandle: this.privateHandle,
          newData: newData
        }).then(function () {
          self.pendingPromiseCount -= 1;
        });
      }
    },

    remove: function() {
      var self = this;
      var service = this.document.service;
      self.pendingPromiseCount += 1;
      self.removed = true;

      delete service.ownCursors[self.privateHandle];
      _.removeOnField("privateHandle", this.document.cursors,
                      this.privateHandle);

      return service.rpcCall("removeCursor", {
        privateHandle: this.privateHandle
      }).then(function () {
        self.pendingPromiseCount -= 1;
      });
    },

    isSynchronized: function() {
      return this.pendingPromiseCount === 0;
    }
  });

  var Document = new Class({
    constructor: function(service, name, cursors) {
      this.service = service;
      this.name = name;

      this.cursors = _.map(cursors, function(cursor) {
        cursor.document = this;
        return new ForeignCursor(cursor);
      }, this);

      this.cursorAdded = new Snorky.Signal();
      this.cursorUpdated = new Snorky.Signal();
      this.cursorRemoved = new Snorky.Signal();
    },

    onCursorAdded: function(cursor) {
      var fatCursor = new ForeignCursor(cursor);
      this.cursors.push(fatCursor);

      this.cursorAdded.dispatch(fatCursor);
    },

    onCursorUpdated: function(cursor) {
      var fatCursor = _.replaceOnField("publicHandle", this.cursors,
                                       cursor);
      this.cursorUpdated.dispatch(fatCursor);
    },

    onCursorRemoved: function(cursor) {
      _.removeOnField("publicHandle", this.cursors, cursor);
      this.cursorRemoved.dispatch(cursor);
    },

    createCursor: function(params) {
      var handle = this.service.getFreePrivateHandle();

      var cursor = new Snorky.Cursors.OwnCursor(this, {
        privateHandle: handle,
        position: params.position,
        status: params.status
      });

      var promise = this.service.rpcCall("createCursor", {
        privateHandle: handle,
        document: this.name,
        position: params.position,
        status: params.status
      }).then(function(publicHandle) {
        cursor.publicHandle = publicHandle;
        cursor.pendingPromiseCount -= 1;
      });

      this.service.ownCursors[handle] = cursor;
      this.cursors.push(cursor);

      return [cursor, promise];
    }
  });

  Snorky.Cursors = new Class(Snorky.RPCService, {
    init: function() {
      Snorky.RPCService.prototype.init.call(this);

      this.notificationReceived.add(this.onNotification, this);

      this.documents = {};
      this.ownCursors = {};
    },

    join: function(params) {
      var self = this;
      return this.rpcCall("join", params)
        .then(function(documentData) {
          var name = params.document;
          var document = new Snorky.Cursors.Document(
            self, name, documentData.cursors);
          self.documents[stableStringify(name)] = document;
          return document;
        });
    },

    onNotification: function(notification) {
      var cursor = notification.cursor;
      var document = this.documents[stableStringify(cursor.document)];
      if (!document) {
        throw Error("Notification for unknown document: " +
                    stableStringify(notification.document));
      }

      if (notification.type == "cursorAdded") {
        document.onCursorAdded(cursor);
      } else if (notification.type == "cursorUpdated") {
        document.onCursorUpdated(cursor);
      } else if (notification.type == "cursorRemoved") {
        document.onCursorRemoved(cursor);
      }
    },

    getFreePrivateHandle: function() {
      if (_.keys(this.ownCursors).length > 100) {
        throw new Error("Too many cursors (thrown at client side)");
      }
      var handle;
      do {
        handle = Math.round(Math.random() * 255);
      } while (handle in this.ownCursors);
      return handle;
    }
  });

  Snorky.Cursors.Document = Document;
  Snorky.Cursors.Cursor = Cursor;
  Snorky.Cursors.ForeignCursor = ForeignCursor;
  Snorky.Cursors.OwnCursor = OwnCursor;

})();


