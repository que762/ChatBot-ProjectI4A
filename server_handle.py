from flask import Flask, render_template
from flask_socketio import SocketIO
import logging

import pipeline

server = Flask(__name__)
server.config['SECRET_KEY'] = 'edubotkey'
# no timeout
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
socketio = SocketIO(server, cors_allowed_origins="*")

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@server.route('/')
def index():
	return render_template('index.html')

@socketio.on('connection')
def connection(msg):
	socketio.emit('ai_message', 'Bonjour, je suis Edubot, comment puis-je vous aider ?')

@socketio.on('disconnection')
def disconnect():
	print('Client disconnected')

@socketio.on('user_message')
def handle_message(msg):
	print('User message:', msg)
	response = pipeline.educhat(msg)
	socketio.emit('ai_message', response)