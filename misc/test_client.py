import socketio
import urllib3

urllib3.disable_warnings()

# Créer une instance du client Socket.IO
sio = socketio.Client(ssl_verify=False, reconnection=True)

# Gestion des événements de connexion
@sio.event
def connect():
    sio.emit("connection", "Hello!")
    print("Connecté au serveur")


# Gestion des événements de déconnexion
@sio.event
def disconnect():
    sio.emit("disconnection", "Goodbye!")
    print("Déconnecté du serveur")

# Gestion des messages
@sio.on("ai_message")
def message(data):
    print("Réponse du serveur :", data)
    if data.lower() == "exit":
        print("\nDéconnexion...")
        sio.disconnect()
    else:
        data = input("Votre message : ")
        sio.emit("user_message", data)



if __name__ == '__main__':
    try:
        # Se connecter au serveur
        sio.connect('https://82.66.33.22:44444')
        # Attendre les événements
        sio.wait()
    except KeyboardInterrupt:
        # Se déconnecter du serveur
        sio.disconnect()