from flask import Flask, render_template
from flask_socketio import SocketIO
import logging
import yaml

import asyncio

import pipeline
import rabbit_functions as RabbitMq

async def process_messages():
    while True:
        request = await RabbitMq.get_last_request(queue_name='messages_users')
        if request:
            user_id = request['user_id']
            user_message = request['message']
            
            # Process the message with your AI
            response_message = await pipeline.educhat(user_id, user_message)
            
            # Send the response back to the queue messages_IA
            response = {'user_id': user_id, 'message': response_message}
            await RabbitMq.send_result(response, queue_name='messages_IA')

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
async def handle_message(msg):
	logger.debug('User message: ' + msg['message'])
	user_id = msg['user_id']
	user_message = msg['message']

    # Envoyer le message à la queue messages_users
	await RabbitMq.send_result({'user_id': user_id, 'message': user_message}, queue_name='messages_users')
	
	await process_messages()

    # Attendre et récupérer la réponse de la queue messages_IA
	response = None
	while response is None:
		response = await RabbitMq.get_last_request(queue_name='messages_IA')

    # Envoyer la réponse à l'utilisateur
	socketio.emit('ai_message', response)