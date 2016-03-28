// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

/*global angular */

/**
 * Service that persists and retrieves tasks from Django API
 */
angular.module('todomvc')
  .config(function(RestangularProvider) {
    function addPatchMethod(obj, propName) {
      var methodName = "patch" + propName[0].toUpperCase() + propName.slice(1);
      obj[methodName] = function(value) {
        if (value === undefined) {
          return obj[propName];
        } else {
          if (obj[propName] != value) {
            obj[propName] = value;
            var delta = {};
            delta[propName] = value;
            obj.save();
          }
        }
      };
    };

    RestangularProvider.setBaseUrl("/api");
    RestangularProvider.setFullResponse(true);

    RestangularProvider.extendCollection("tasks", function(collection) {
      collection.getListAndSubscription = function(queryParams, headers) {
        headers = headers || {};
        headers["X-Snorky"] = "Subscribe";

        return this.getList(queryParams || {}, headers)
        .then(function(response) {
          response.subscriptionToken = response.headers("X-Subscription-Token");
          return response;
        });
      };

      return collection;
    });

    RestangularProvider.extendModel("tasks", function(model) {
      addPatchMethod(model, "title");
      addPatchMethod(model, "completed");

      return model;
    })
  })
	.factory('todoStorage', function (Restangular) {
    var snorky = new Snorky(WebSocket, "ws://localhost:5001/ws", {
      "datasync": Snorky.DataSync
    });
    var deltaProcessor = new Snorky.DataSync.CollectionDeltaProcessor();
    snorky.services.datasync.onDelta = function(delta) {
      // Called each time a data change notification (delta) is received.
      // CollectionDeltaProcessor is a class that applies these deltas
      // in a collection (usually an array).
      deltaProcessor.processDelta(delta);

      // Here we could also inspect the delta element and show alerts to the
      // user or play a sound when data changes.
    };

    var tasks = Restangular.all("tasks").getListAndSubscription()
    .then(function(response) {
      var taskArray = response.data;

      // A collection wraps an array over an interface which is understood
      // by deltaProcessor.
      //
      // e.g. when an insertion delta is received, deltaProcessor will push
      // an element in the collection.
      //
      var taskCollection = new Snorky.DataSync.ArrayCollection(taskArray, {
        transformItem: function(item) {
          // Allows us to define how a data element received from a delta as
          // simple JSON will be translated to an element of this array.

          // This is useful if we use fat elements (e.g. each element has a
          // .delete() method).
          return Restangular.restangularizeElement(
            null, item, "tasks", true, response.data, null
          );
        }
      })

      // Tell the collection delta processor: updates of elements of class Task
      // should be applied to taskCollection.
      deltaProcessor.collections["Task"] = taskCollection;

      // Send our new subscription token to Snorky, so that we can receive
      // notifications for changes in tasks.
      snorky.services.datasync.acquireSubscription({
        token: response.subscriptionToken
      });

      // Return the array, which will be automatically updated thanks to
      // Snorky deltaProcessor.
      return taskArray;
    });

    return tasks;
	});
