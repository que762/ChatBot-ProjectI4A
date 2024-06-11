import socketio
import eventlet
import ssl
import logging

# Create a Socket.IO server
sio = socketio.Server(logger=True, engineio_logger=True)

# Create a WSGI application
app = socketio.WSGIApp(sio)

# Setup logging
logging.basicConfig(level=logging.INFO)

@sio.event
def connect(sid, environ):
    logging.info(f'Client connected: {sid}')

@sio.event
def disconnect(sid):
    logging.info(f'Client disconnected: {sid}')

@sio.event
def message(sid, data):
    if isinstance(data, str):
        logging.info(f'Message from client: {data}')
        sio.emit('message', 'Your message was received by the server', room=sid)
    else:
        logging.warning(f'Invalid message format from {sid}')

# Create an SSL context with enhanced security
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile='secure_connection/finalCertProject.crt', keyfile='secure_connection/privateKeyProject.key')

# Create and wrap the socket with SSL
server_socket = eventlet.listen(('0.0.0.0', 5000))
ssl_socket = ssl_context.wrap_socket(server_socket, server_side=True)

# Start the server
if __name__ == '__main__':
    eventlet.wsgi.server(ssl_socket, app)
