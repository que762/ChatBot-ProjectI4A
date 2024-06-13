import torch
import yaml
import logging

import utils.formation_dataset as formation_dataset
import utils.fetch_parcoursup as fetch_parcoursup
import utils.fire_db as fire_db
import edubot

# Config
config = yaml.safe_load(open("config.yaml"))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
prompt_path = config["directories"]["prompt"]
prompt = open(prompt_path, "r").read()

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(config["log_level"])


def find_best_schools(user_id, sentence):
    # Convert for better accuracy
    prepas = ["prépa", "classes préparatoires", "classes prépa"]
    for prepa in prepas:
        if prepas in sentence:
            sentence = sentence.replace(prepa, "CPGE")

    if "distanciel" in sentence:
        sentence = sentence.replace("distanciel", "à distance")


    similarities = formation_dataset.compare_to_each_row(sentence)
    sorted_formations = formation_dataset.sort_by_most_similar(similarities)

    if sorted_formations is None:
        response = "Désolé, je n'ai pas trouvé de formation correspondant à votre recherche."
        fire_db.add_message(user_id, response, is_bot=True)
        return response, None
    
    else:
        formations = sorted_formations.head(5)

        logger.debug("Found formations:")
        logger.debug(formations['description'])

        id_f = 1
        input_text = "Tu as trouvé ces formations. Donne la liste numérotée de toutes ces formations et explique ce que chacune propose.\n"
        context = ""
        for index, formation in formations.iterrows():
            context += f" - {id_f} : {formation['description']}\n"
            id_f += 1

        return edubot.chat_db(user_id, input_text, context=context), formations
    
def get_school_info(user_id, input_text, url, description):

    context = description + "\n" + str(fetch_parcoursup.fetch_parcourSup(url))

    if context is None:
        input_text = "Tu n'as pu trouver aucune information sur la formation. Peux-tu me donner plus de détails sur la formation avec ta base de connaissances ?"
    
    return edubot.chat_db(user_id, input_text, context=context)