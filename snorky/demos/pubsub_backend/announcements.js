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
