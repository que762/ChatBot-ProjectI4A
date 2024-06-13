from flask import Flask, render_template
from flask_socketio import SocketIO
import logging
import yaml

import pipeline
import utils.mongo as mongo

server = Flask(__name__)
server.config['SECRET_KEY'] = 'edubotkey'
# no timeout
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
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
    socketio.emit('ai_message', 'Bonjour, je suis Edubot, comment puis-je vous aider ?')


@socketio.on('disconnection')
def disconnect(msg):
    logger.info('User disconnected')


@socketio.on('user_message')
def handle_message(msg):
    logger.debug('User message: ' + msg['message'])
    user_id = msg['user_id']
    user_message = msg['message']

    response = pipeline.educhat(user_id, user_message)

    # Save the conversation
    mongo.insert_message(user_id, user_message, is_bot=False)
    mongo.insert_message(user_id, response, is_bot=True)

    # Send the response to the user
    socketio.emit('ai_message', response)
