from __future__ import unicode_literals
from collections import defaultdict
import gevent

class PubSubBackend(object):
    def __init__(self, redis, socket, channel, logger):
        self.redis = redis
        self.socket = socket
        self.channel = channel
        self.logger = logger

        self.pubsub = redis.pubsub()
        self.unsubscribed = False

    def unsubscribe(self):
        self.unsubscribed = True

    def __iter_data(self):
        for message in self.pubsub.listen():
            if self.unsubscribed:
                self.logger.debug('(redis) [UNSUBSCRIBE] {0}'.format(self.channel))
                self.pubsub.unsubscribe(self.channel)
            if message.get('type') == 'message':
                data = message.get('data')
                channel = message.get('channel')
                self.logger.debug('(redis) [MESSAGE] {0}: {1}'.format(channel,
                    data))
                if channel == self.channel:
                    yield (data)

    def _send(self, socket, data):
        try:
            socket.send(data)
        except Exception: # TODO: don't catch base exception
            self.sockets.remove(socket)

    def run(self):
        self.logger.debug('(redis) [SUBSCRIBE] {0}'.format(self.channel))
        self.pubsub.subscribe(self.channel)
        for data in self.__iter_data():
            self.logger.debug('(socket) [MESSAGE] {0}: {1}'.format(self.channel,
                data))
            gevent.spawn(self._send, self.socket, data)

    def start(self):
        gevent.spawn(self.run)
