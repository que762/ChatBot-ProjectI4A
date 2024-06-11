import requests
from bs4 import BeautifulSoup

# URL de la page web
# url = "https://dossierappel.parcoursup.fr/Candidats/public/fiches/afficherFicheFormation?g_ta_cod=479"

def call_to_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Erreur lors de la requête HTTP: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête HTTP: {e}")
        return None

    return response

def fetch_parcourSup(url):
    # Appel de la page web
    response = call_to_url(url)

    # Si la réponse est vide, on arrête l'exécution de la fonction
    if not response:
        return None

    # Parser le contenu HTML de la page web
    soup = BeautifulSoup(response.text, 'html.parser')

    # On test si la page web contient le texte "Erreur 404!". Si c'est le cas, on arrête l'exécution de la fonction
    if soup.find(string='Erreur 404!'):
        return None

    #print(soup.prettify())

    # Liste des informations à récupérer
    formation_info = {}

    # Récupération des informations sur la formation
    # On recherche la balise h3 qui contient "Présentation de la formation"
    presentation_section = soup.find('h3', string='Présentation de la formation')
    try:
        if presentation_section:
            # Extraction de tous les paragraphes situés dans la balise div de classe "word-break-break-word"
            formation_info['presentation'] = presentation_section.find_next('div', class_='word-break-break-word').get_text()
    except AttributeError:
        pass

    # Récupération des informations sur les frais de candidature et d'inscription
    frais_section = soup.find('h3', string="Frais de candidature")
    try:
        if frais_section:
            #Récupére tous les texte de la balise div de classe "fr-callout fr-callout--blue-cumulus"
            formation_info['frais'] = frais_section.find_previous().get_text()
    except AttributeError:
        pass

    # Récupération des informations sur les poursuites d'études
    poursuite_section = soup.find('h3', string="Poursuite d'études")
    try:
        if poursuite_section:
            #Extraction de tous les paragraphes situés dans la balise div de classe "word-break-break-word"
            formation_info['poursuite_etu'] = poursuite_section.find_previous().get_text()
    except AttributeError:
        pass

    # Récupération des informations sur les débouchés
    debouche_section = soup.find('h3', string="Débouchés professionnels")
    try:
        if debouche_section:
            #Extraction de tous les paragraphes situés dans la balise div de classe "word-break-break-word"
            formation_info['debouche'] = debouche_section.find_next('div', class_='word-break-break-word').get_text()
    except AttributeError:
        pass

    # Nettoyage des informations récupérées
    # On retire tous les caractères spéciaux de la chaine de caractère (comme les espaces, les tabulations, les retours à la ligne, etc.)
    # On vérifie également si la chain
    if 'presentation' in formation_info:
        formation_info['presentation'] = ' '.join(formation_info['presentation'].split())
    if 'frais' in formation_info:
        formation_info['frais'] = ' '.join(formation_info['frais'].split())
    if 'poursuite_etu' in formation_info:
        formation_info['poursuite_etu'] = ' '.join(formation_info['poursuite_etu'].split())
    if 'debouche' in formation_info:
        formation_info['debouche'] = ' '.join(formation_info['debouche'].split())

    return formation_info

# Appel de la fonction fetch_parcourSup
# formation_info = fetch_parcourSup(url)
# if formation_info:
#    print(formation_info)
