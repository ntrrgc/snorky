// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

/*global angular */

/**
 * Services that persists and retrieves tasks from Django API
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
      deltaProcessor.processDelta(delta);
    }

    var tasks = Restangular.all("tasks").getListAndSubscription()
    .then(function(response) {
      // Tell Snorky where to put the updated data
      deltaProcessor.collections["Task"] =
        new Snorky.DataSync.ArrayCollection(response.data, {
          transformItem: function(item) {
            // We use fat ORM - style objects, so we need to specify a
            // transformation function that constructs one of our fat objects
            // from a simple JSON one.
            return Restangular.restangularizeElement(
              null, item, "tasks", true, response.data, null
            );
          }
        });

      // Tell Snorky our new subscription token
      snorky.services.datasync.acquireSubscription({
        token: response.subscriptionToken
      });

      // Return the data innocently
      return response.data;
    });

    return tasks;
	});
