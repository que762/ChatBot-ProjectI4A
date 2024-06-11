# server.py
from flask import Flask, render_template
from flask_socketio import SocketIO
server = Flask(__name__)
server.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(server)
@server.route('/')
def index():
	return render_template('index.html')
@socketio.on('message')
def handle_message(msg):
	print('Message received: ' + msg)
	socketio.send('Message: ' + msg)
if __name__ == '__main__':
	socketio.run(server)