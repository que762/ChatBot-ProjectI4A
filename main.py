import torch

import chatbot
import vigogne
import utils.question_classification as classif
import utils.formation_dataset as formation_dataset

latest_found_schools = []

print("CUDA version used is : " + torch.version.cuda)
print("Total GPU memory is : " + str(torch.cuda.get_device_properties(0).total_memory / 1024**3) + " GB")
print("Total GPU memory used is : " + str(torch.cuda.memory_allocated(0) / 1024**3) + " GB")
print("Total GPU memory cached is : " + str(torch.cuda.memory_reserved(0) / 1024**3) + " GB")
print("Total GPU memory free is : " + str((torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3) + " GB")

def educhat(input_text : str):
    global latest_found_schools

    question_class = classif.classify(input_text)
    print("Detected question class: " + question_class)

    if question_class == "search_schools":
        response, formations = chatbot.find_best_schools(input_text)
        latest_found_schools = formations
        return response[0]
    
    elif question_class == "school_info":
        # If latest question wasn't about searching schools
        if len(latest_found_schools) == 0:
            return vigogne.chat(input_text)[0]
        else :
            similarities = formation_dataset.compare_to_each_row(input_text)
            sorted_formations = formation_dataset.sort_by_most_similar(similarities)
            
            if sorted_formations is None:
                return "Désolé, je n'ai pas trouvé de formation correspondant à votre recherche."
            else:
                print(sorted_formations.iloc[0])
                return chatbot.get_school_info(input_text, sorted_formations.iloc[0]['url'])[0]

    else:
        latest_found_schools = []
        return vigogne.chat(input_text)[0]

if __name__ == "__main__":
    while True:
        input_text = input("> ")
        print(educhat(input_text))