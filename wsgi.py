# wsgi.py
from server_handle import server, socketio
if __name__ == "__main__":
    socketio.run(server)