import torch
import yaml

import utils.formation_dataset as formation_dataset
import vigogne

config = yaml.safe_load(open("config.yaml"))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
prompt_path = config["directories"]["prompt"]
prompt = open(prompt_path, "r").read()

def find_best_schools(sentence):
    similarities = formation_dataset.compare_to_each_row(sentence)
    sorted_formations = formation_dataset.sort_by_most_similar(similarities)

    if sorted_formations is None:
        return "Désolé, je n'ai pas trouvé de formation correspondant à votre recherche."

    else:
        formations = sorted_formations.head(5)
        id_f = 1
        input_text = "Tu as trouvé les formations précédentes. Donne la liste numérotée de ces formations et détaille ce qu'elles proposent.\n"
        context = ""
        for index, formation in formations.iterrows():
            context += f" - {id_f} : {formation['description']}\n"
            id_f += 1

        return vigogne.chat(input_text, context=context)