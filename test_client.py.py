import socketio
import ssl

# Chemin vers le certificat auto-signé
ssl_cert_path = 'secure_connection/finalCertProject.crt'

# Créer un contexte SSL
ssl_context = ssl.create_default_context()

# Charger le certificat auto-signé
ssl_context.load_verify_locations(cafile=ssl_cert_path)

# Créer un client Socket.IO en spécifiant le contexte SSL personnalisé
sio = socketio.Client(logger=True, engineio_logger=True, ssl_verify=ssl_context)

connected = False

@sio.event
def connect():
    global connected
    connected = True
    print("Connected to the server")

@sio.event
def connect_error(data):
    print("Failed to connect to the server")

@sio.event
def disconnect():
    global connected
    connected = False
    print("Disconnected from the server")

@sio.event
def message(data):
    print(f"Message from server: {data}")

# Connect to the server
sio.connect('https://192.168.226.204:5000')

while True:
    if connected:
        message = input("Enter a message ('exit' to quit): ")
        if message.lower() == 'exit':
            sio.disconnect()
        sio.send(message)

# Wait for messages and keep the connection alive until the user decides to exit
sio.wait()