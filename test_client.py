import socketio
import urllib3

urllib3.disable_warnings()

# Create a Socket.IO client
sio = socketio.Client(ssl_verify=False, reconnection=True)


# Event handlers
@sio.event
def connect():
    sio.emit("connection", "Hello!")
    print("Connected to the server")


@sio.event
def disconnect():
    sio.emit("disconnection", "Goodbye!")
    print("Disconnected from the server")


# Message handler
@sio.on("ai_message")
def message(data):
    print("Server Answer:", data)
    if data.lower() == "exit":
        print("\nDisconnection...")
        sio.disconnect()
    else:
        data = input("Your msg : ")
        user_message = {"user_id": "123", "message": data}
        sio.emit("user_message", user_message)


if __name__ == '__main__':
    try:
        sio.connect('https://82.66.33.22:44444')
        sio.wait()
    except KeyboardInterrupt:
        sio.disconnect()
