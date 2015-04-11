// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

"use strict";

angular.module("Announcements", ["Snorky"])
  .controller("AnnouncementsCtrl", function($scope) {
    $scope.snorky = new Snorky(WebSocket, "ws://" + location.host + "/ws", {
      "pubsub": Snorky.PubSub
    }, true);

    $scope.snorky.services.pubsub.subscribe({ channel: "announcements" });

    $scope.announcements = [];

    $scope.snorky.services.pubsub.onMessagePublished = function(msg) {
      $scope.announcements.push(msg.message);
    };
  });
