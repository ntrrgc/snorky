var SimplePubSub = new Snorky.Class(Snorky.RPCService, {
  init: function() {
    // Call the superclass init()
    Snorky.RPCService.prototype.init();

    // Listen notificationReceived events
    this.notificationReceived.add(this.onNotification, this);

    // Create new event
    this.publicationReceived = new Snorky.Signal();
  },

  onNotification: function(notification) {
    if (notification.type == "publication") {
      // Dispatch the publicationReceived event
      this.publicationReceived.dispatch(notification.message);
    }
  }
});
SimplePubSub.addRPCMethods([
  "subscribe",
  "unsubscribe",
  "publish"
]);
