import socketio
import eventlet

# Create a Socket.IO server
sio = socketio.Server()

# Create a WSGI application
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

@sio.event
def message(sid, data):
    print('Message from client:', data)
    sio.emit('message', 'Your message was received by the server', room=sid)

# Start the server
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('192.168.226.204', 5000)), app)
