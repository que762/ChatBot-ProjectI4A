import logging
import yaml

import chatbot
import edubot
import utils.question_classification as classif
import utils.formation_dataset as formation_dataset

# Logging
conf = yaml.safe_load(open("config.yaml"))
logger = logging.getLogger(__name__)
logger.setLevel(conf["log_level"])

latest_found_schools = []

def educhat(user_id, input_text : str):
    global latest_found_schools

    question_class = classif.classify(input_text)
    logger.debug("Detected question class: " + question_class)

    # Search for schools
    if question_class == "search_schools":
        response, formations = chatbot.find_best_schools(user_id, input_text)
        latest_found_schools = formations
        return response[0]
    
    # Get school info
    elif question_class == "school_info":
        # If latest question wasn't about searching schools, fallback
        if len(latest_found_schools) == 0:
            return edubot.chat_db(user_id, input_text)[0]
        else :
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
                return chatbot.get_school_info(user_id, input_text, sorted_formations.iloc[0]['url'], sorted_formations.iloc[0]['description'])[0]

    # Open questions
    else:
        latest_found_schools = []
        return edubot.chat_db(user_id, input_text)[0]
