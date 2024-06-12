import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import yaml
import logging

# config
config = yaml.safe_load(open("config.yaml"))
logger = logging.getLogger(__name__)
logger.setLevel(config["log_level"])

logger.info("Connecting to Firebase...")
cred = credentials.Certificate(config['firebase_creds'])
firebase_admin.initialize_app(cred)
db = firestore.client()
logger.info("Connected to Firebase\n")

def find_message_by_user(user_id):
    return db.collection('messages').where('user', '==', user_id).get()

def retrieve_convo(user_id):
    messages = find_message_by_user(user_id)

    # sort messages by timestamp
    messages = sorted(messages, key=lambda x: x.to_dict()['timestamp'])

    convo = []
    for message in messages:
        if message.to_dict()['message']['type'] == 'ia':
            convo.append({'role': 'assistant','content': message.to_dict()['message']['message']})
        else:
            convo.append({'role': 'user','content': message.to_dict()['message']['message']})
    return convo

def add_message(user_id, message, is_bot=False):
    db.collection('messages').add({
        'message':{
            'message': message,
            'type': 'ia' if is_bot else 'user'
        },
        'timestamp': firestore.SERVER_TIMESTAMP,
        'user': user_id
    })
    logger.debug(f"Added message to user {user_id}: {message}")

if __name__ == "__main__":
    convo = retrieve_convo('jupQXBfzgcc5IJDEQOg8wV3xhml1')
    for message in convo:
        print(message)

    logger.info("test")
    logger.debug("Adding test messages...")

    # add_message('jupQXBfzgcc5IJDEQOg8wV3xhml1', 'Python test')
    # add_message('jupQXBfzgcc5IJDEQOg8wV3xhml1', 'Python test 2', is_bot=True)