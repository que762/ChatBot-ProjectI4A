import socketio
import urllib3

urllib3.disable_warnings()

# Créer une instance du client Socket.IO
sio = socketio.Client(ssl_verify=False)

# Gestion des événements de connexion
@sio.event
def connect():
    print("Connecté au serveur")
    sio.send("Bonjour serveur!")

# Gestion des événements de déconnexion
@sio.event
def disconnect():
    print("Déconnecté du serveur")

# Gestion des messages
@sio.event
def message(data):
    while True :
        print("Réponse du serveur :", data)
        if data.lower() == "exit":
            print("\nDéconnexion...")
            sio.disconnect()
            break
        else:
            data = input("Votre message : ")
            sio.emit("message", data)



if __name__ == '__main__':
    try:
        # Se connecter au serveur
        sio.connect('https://asile.freeboxos.fr:44444')
        # Attendre les événements
        sio.wait()
    except KeyboardInterrupt:
        # Se déconnecter du serveur
        sio.disconnect()