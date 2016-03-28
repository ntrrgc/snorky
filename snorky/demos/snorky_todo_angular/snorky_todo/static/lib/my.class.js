/*
my.class.js
25e7718fe8 (4 Jun 2013)
https://github.com/jiem/my-class

Copyright (c) 2011 Jie Meng-Gerard

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

/*globals define:true, window:true, module:true*/
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
