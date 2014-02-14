from __future__ import unicode_literals
import logging
import os
from collections import defaultdict

import anyjson
import gevent
import redis
from flask import Flask, render_template, request
from flask_sockets import Sockets
from geventwebsocket.exceptions import WebSocketError

from tasks import MyTask
from pubsub import PubSubBackend

REDIS_URL = os.environ.get('REDISCLOUD_URL', 'redis://localhost:6379')

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

sockets = Sockets(app)
redis_client = redis.from_url(REDIS_URL)

def receive_message(ws):
    while not ws.closed:
        gevent.sleep()
        try:
            data = ws.receive()
        except WebSocketError:
            app.logger.error('Websocket went away while trying to read')
            return

        if data:
            try:
                return anyjson.loads(data)
            except ValueError:
                app.logger.error('Failed to json decode message: {0}'.format(data))

@app.route('/')
def index():
    result = MyTask().delay()
    return render_template('index.html', task_id=result.id)

@sockets.route('/subscribe')
def subscribe(ws):
    message = receive_message(ws)
    channel = message.get('channel')

    if channel:
        backend = PubSubBackend(redis_client, ws, channel, app.logger)
        backend.start()

        # In order to detect that the websocket closed, we must be actively
        # trying to receive data on it.
        while receive_message(ws):
            gevent.sleep()

        app.logger.debug('Websocket closed, unsubscribing')
        backend.unsubscribe()
