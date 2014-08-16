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
