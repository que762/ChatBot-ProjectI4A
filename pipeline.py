import logging
import yaml

import edubot
import utils.question_classification as classif
import utils.formation_dataset as formation_dataset
import utils.fetch_parcoursup as fetch_parcoursup

# Logging
conf = yaml.safe_load(open("config.yaml"))
logger = logging.getLogger(__name__)
logger.setLevel(conf["log_level"])

latest_found_schools = []


def educhat(user_id, input_text: str):
    global latest_found_schools

    question_class = classif.classify(input_text)
    logger.debug("Detected question class: " + question_class)

    # Search for schools
    if question_class == "search_schools":
        response, formations = find_best_schools(user_id, input_text)
        latest_found_schools = formations
        return response[0]

    # Get school info
    elif question_class == "school_info":
        # If latest question wasn't about searching schools, fallback
        if len(latest_found_schools) == 0:
            return edubot.chat_db(user_id, input_text)[0]
        else:
            embeddings = []
            for row in latest_found_schools.iterrows():
                index = formation_dataset.find_index_by_description(row[1]['description'])
                embeddings.append(formation_dataset.get_row_embedding(index))

            similarities = formation_dataset.compare_to_each_row(input_text, embeddings)
            sorted_formations = formation_dataset.sort_by_most_similar(similarities, latest_found_schools)

            if sorted_formations is None:
                return "Désolé, je n'ai pas trouvé de formation correspondant à votre recherche."
            else:
                logger.debug("Most similar formation:")
                logger.debug(sorted_formations.iloc[0]['description'], sorted_formations.iloc[0]['url'])
                return get_school_info(user_id, input_text, sorted_formations.iloc[0]['url'],
                                       sorted_formations.iloc[0]['description'])[0]

    # Open questions
    else:
        latest_found_schools = []
        return edubot.chat_db(user_id, input_text)[0]


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
        return response, None

    else:
        formations = sorted_formations.head(5)

        logger.debug("Found formations:")
        logger.debug(formations['description'])

        id_f = 1
        input_text = ("Tu as trouvé ces formations. Donne la liste numérotée de toutes ces formations et explique ce "
                      "que chacune propose.\n")
        context = ""
        for index, formation in formations.iterrows():
            context += f" - {id_f} : {formation['description']}\n"
            id_f += 1

        return edubot.chat_db(user_id, input_text, context=context), formations


def get_school_info(user_id, input_text, url, description):
    context = description + "\n" + str(fetch_parcoursup.fetch_parcourSup(url))

    if context is None:
        input_text = ("Tu n'as pu trouver aucune information sur la formation. Peux-tu me donner plus de détails sur "
                      "la formation avec ta base de connaissances ?")

    return edubot.chat_db(user_id, input_text, context=context)
