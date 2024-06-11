# wsgi.py
from server import server, socketio
if __name__ == "__main__":
    socketio.run(server)