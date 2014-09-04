Using Snorky with AngularJS
===========================

If you use AngularJS you can benefit from Angular Snorky. If you don't, you can skip this.

Angular Snorky is a small library which modifies Snorky to use ``$q`` promises instead of ES6 promises and automatically triggers ``$digest`` cycles on event dispatching.

Using Angular Snorky
~~~~~~~~~~~~~~~~~~~~

In order to use Angular Snorky you need to include ``angular-snorky.js`` after both ``angular.js`` and ``snorky.js``.

Then, you need to add it to the dependencies of your application.

.. code-block:: javascript

    angular.module("my-app", [
      /* other dependencies */
      "Snorky"
    ])

After that, the usage of Snorky is exactly the same, you keep on using the Snorky object exported in the global object.
