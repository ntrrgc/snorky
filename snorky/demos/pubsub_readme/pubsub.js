var snorky = new Snorky(WebSocket, "ws://localhost:8002/websocket", {
  "pubsub": Snorky.PubSub
});
var pubsub = snorky.services.pubsub;

pubsub.subscribe({channel: 'messages'})
.then(function() {
  // Confirmation received! (optional)
});

pubsub.messagePublished.add(function(messageObject) {
  $('#messages').append(
    $('<li/>', {
    text: messageObject.message
  }));
});

$('form').on('submit', function(event) {
  event.preventDefault(); // don't reload the page

  pubsub.publish({
    channel: 'messages',
    message: $('#message').val()
  });
});
