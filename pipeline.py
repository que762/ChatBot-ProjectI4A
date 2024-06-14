import logging
import yaml

import edubot
import utils.question_classification as q_classification
import utils.formation_dataset as formation_dataset
import utils.fetch_parcoursup as fetch_parcoursup
import utils.mongo as mongo

# Logging
conf = yaml.safe_load(open("config.yaml"))
logger = logging.getLogger(__name__)
logger.setLevel(conf["log_level"])
logging.basicConfig(level=conf["log_level"])

latest_found_schools = []


def educhat(user_id, input_text: str):
    """Main pipeline function for the educational chatbot. \n
    There are three possible classes of questions: \n
    - search_schools: The user is searching for schools. \n
    - school_info: The user is asking for information about a specific school. \n
    - open_question: The user is asking an open question. \n
    The function classifies the question and returns the bot response.

    :param user_id: The user ID.
    :param input_text: The user input text.
    :return: The bot response."""

    global latest_found_schools

    # Convert some words for better classification
    prepas = ["prépa", "classes préparatoires", "classes prépa", "prepa"]
    for prepa in prepas:
        if input_text.find(prepa) != -1:
            input_text = input_text.replace(prepa, "CPGE")

    if input_text.find("distanciel") != -1:
        input_text = input_text.replace("distanciel", "à distance")

    # Classify the question
    question_class = q_classification.classify(input_text)
    logger.debug(f"Question class: {question_class}")

    # Question : search_schools
    if question_class == "search_schools":
        response, formations = find_best_schools(user_id, input_text)
        if formations is not None:
            latest_found_schools = formations
        else:
            latest_found_schools = []
        return response[0]

    # Question : school_info
    elif question_class == "school_info":
        # If latest question wasn't about searching schools, fallback
        if len(latest_found_schools) == 0:
            return edubot.chat_db(user_id, input_text)[0]
        else:
            # Get the most similar formation
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
                logger.debug(sorted_formations.iloc[0]['description'] + sorted_formations.iloc[0]['url'])
                return get_school_info(user_id, input_text, sorted_formations.iloc[0]['url'],
                                       sorted_formations.iloc[0]['description'])[0]

    # Open questions
    else:
        latest_found_schools = []
        return edubot.chat_db(user_id, input_text)[0]


def find_best_schools(user_id, sentence):
    """Function used by the pipeline to find the best schools for a given sentence.
    :param user_id: The user ID.
    :param sentence: The user input sentence.
    :return: The bot response and the found schools."""

    # Compare the sentence to each formation in the dataset
    similarities = formation_dataset.compare_to_each_row(sentence)
    sorted_formations = formation_dataset.sort_by_most_similar(similarities)

    # If no formation was found
    if sorted_formations is None:
        return edubot.chat_db(user_id, sentence), None

    # If at least one formation was found, return the top 5
    else:
        formations = sorted_formations.head(5)

        logger.debug("Found formations:")
        logger.debug(formations['description'])

        id_f = 1
        input_text = ("Liste chacune des formations du contexte et explique en détail ce "
                      "que chacune propose.\n")
        context = ""
        for index, formation in formations.iterrows():
            context += f" - {id_f} : {formation['description']}\n"
            id_f += 1

        return edubot.chat_db(user_id, input_text, context=context), formations


def get_school_info(user_id, input_text, url, description):
    """Function used by the pipeline to get information about a specific school.
    The previous question must have been about searching schools, otherwise it will fall back to the default chat.
    :param user_id: The user ID.
    :param input_text: The user input text.
    :param url: The URL of the school page.
    :param description: The description of the school.
    :return: The bot response."""

    # Fetch the information from the URL
    try:
        context = description + "\n" + str(fetch_parcoursup.fetch_parcoursup(url))
        context += "\n Pour plus d'informations, lien vers la fiche de formation: " + url

    # If the school page couldn't be fetched
    except:
        input_text = ("Tu n'as pu trouver aucune information sur la formation. Peux-tu me donner plus de détails sur "
                      "la formation avec ta base de connaissances ?")
        context = None

    return edubot.chat_db(user_id, input_text, context=context)


# Testing
if __name__ == "__main__":
    user_id_test = "1234"
    mongo.clear_db()
    while True:
        user_input = input("User: ")
        bot_response = educhat(user_id_test, user_input)
        print("Bot: " + bot_response)
        mongo.insert_message(user_input, user_id_test, False)
        mongo.insert_message(bot_response, user_id_test, True)
