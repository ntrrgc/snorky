"use strict";

angular.module("Chat", ["ui.bootstrap", "Snorky"])
  .service("SnorkyChat", function($rootScope) {
    var self = this;

    this.snorky = new Snorky(WebSocket, "ws://" + location.host + "/ws", {
      "messaging": Snorky.Messaging
    }, true);
    var messaging = this.snorky.services.messaging;

    this.myName = null;
    this.conversations = [];
    this.registered = false;

    this.registerName = function(name) {
      return messaging.registerParticipant({
        "name": name
      }).then(function() {
        self.registered = true;
        self.myName = name;
      });
    };

    this.ensureConversation = function(participantName) {
      return _.ensure(self.conversations, function(c) {
        return c.participantName == participantName;
      }, {
        "participantName": participantName,
        "messages": []
      });
    };

    messaging.onParticipantMessage = function(sender, dest, body) {
      var conversation = self.ensureConversation(sender);
      conversation.messages.push({
        "sender": sender,
        "body": body
      });
    };

    this.sendMessage = function(conversation, destName, body) {
      return messaging.send({
        "sender": self.myName,
        "dest": destName,
        "body": body
      }).then(function() {
        conversation.messages.push({
          "sender": self.myName,
          "body": body
        });
      });
    };

  })
  .controller("ChatCtrl", function($scope, SnorkyChat) {
    $scope.chat = SnorkyChat;
    $scope.myName = "";
    $scope.registerError = "";

    $scope.registerName = function(name) {
      $scope.registerError = "";
      return $scope.chat.registerName(name).catch(function(err) {
        $scope.registerError = err.message;
      });
    };

    $scope.addBuddy = function(buddyName) {
      var conversation = $scope.chat.ensureConversation(buddyName);
      conversation.selected = true;
    };

    $scope.sendMessage = function(conversation, body) {
      conversation.sendError = "";
      var dest = conversation.participantName;
      var body = conversation.writtenMessage;
      return $scope.chat.sendMessage(conversation, dest, body)
        .catch(function(err) {
          conversation.sendError = err.message;
        });
    };
  })
