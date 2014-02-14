PubSub = function(websocketUrl) {
  this.websocketUrl = websocketUrl
  this.sockets = {};
  this.handlers = {};

  return this;
}
PubSub.prototype.subscribe = function(channel) {
  if (!this.sockets[channel]) {
    var socket = new ReconnectingWebSocket(this.websocketUrl + '/subscribe');
    socket.onopen = function() {
      socket.send(JSON.stringify({channel: channel}));
      this.sockets[channel] = socket;
    }.bind(this);

    socket.onmessage = function(event) {
      message = JSON.parse(event.data);
      handlers = this.handlers[message.channel] || [];
      handlers.forEach(function(handler) {
        handler(message.data);
      });
    }.bind(this);
  }

  return this;
}
PubSub.prototype.addHandler = function(channel, handler) {
  if (!this.handlers[channel]) {
    this.handlers[channel] = [];
  }
  this.handlers[channel].push(handler);

  return this;
}
