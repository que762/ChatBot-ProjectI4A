from flask import Flask, render_template, request
from flask_socketio import SocketIO
import logging
import yaml

import pipeline
import utils.mongo as mongo

server = Flask(__name__)
server.config['SECRET_KEY'] = 'edubotkey'
socketio = SocketIO(server, cors_allowed_origins="*")

# Logging
conf = yaml.safe_load(open("config.yaml"))
logger = logging.getLogger(__name__)
logger.setLevel(conf["log_level"])


@server.route('/')
def index():
    return render_template('index.html')


@socketio.on('connection')
def connection(msg):
    socket_id = request.sid
    socketio.emit('ai_message', 'Bonjour, je suis StudyMate, comment puis-je vous aider ?', to=socket_id)


@socketio.on('disconnection')
def disconnect(msg):
    logger.info('User disconnected')


@socketio.on('user_message')
def handle_message(msg):
    logger.debug('User message: ' + msg['message'])
    user_id = msg['user_id']
    user_message = msg['message']
    socket_id = request.sid

    response = pipeline.educhat(user_id, user_message)

    # Save the conversation
    mongo.insert_message(user_message, user_id, is_bot=False)
    mongo.insert_message(response, user_id, is_bot=True)

    # Send the response to the user
    socketio.emit('ai_message', response, to=socket_id)
