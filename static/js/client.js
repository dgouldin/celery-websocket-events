PubSub = function(websocketUrl) {
  this.websocketUrl = websocketUrl
  this.sockets = {};
  this.callbacks = {};
}
PubSub.prototype.subscribe = function(channel, callback) {
  if (!this.sockets[channel]) {
    var socket = new ReconnectingWebSocket(this.websocketUrl + '/subscribe');
    socket.onopen = function() {
      socket.send(JSON.stringify({channel: channel}));
      this.sockets[channel] = socket;
    }.bind(this);

    socket.onmessage = function(event) {
      console.log('event', event);
    }
  }
}

var pubsub = new PubSub('ws://' + location.host);
