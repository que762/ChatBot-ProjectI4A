from flask import Flask, render_template
from flask_socketio import SocketIO
import logging
import yaml

import pipeline
#import vigogne

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
	socketio.emit('ai_message', 'Bonjour, je suis Edubot, comment puis-je vous aider ?')

@socketio.on('disconnection')
def disconnect(msg):
	logger.info('User disconnected')

@socketio.on('user_message')
def handle_message(msg):
	logger.debug('User message: ' + msg['message'])
	response = pipeline.educhat(msg['user_id'], msg['message'])
	#response, _ = vigogne.chat(msg['message'])
	socketio.emit('ai_message', response)