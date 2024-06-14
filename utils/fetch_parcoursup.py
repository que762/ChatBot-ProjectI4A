import requests
from bs4 import BeautifulSoup

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def call_to_url(url):
    """Get the content of a webpage.
    :param url: The URL of the webpage.
    :return: The response object."""

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erreur lors de la requête HTTP: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête HTTP: {e}")
        return None

    return response


def fetch_parcoursup(url):
    """Function to fetch information about a school from the Parcoursup website.
    :param url: The URL of the school page.
    :return: A dictionary containing the information about the school."""

    # Get the content of the webpage
    response = call_to_url(url)

    # If the response is empty, return None
    if not response:
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # If the page is a 404 error page, return None
    if soup.find(string='Erreur 404!'):
        return None

    # Fetch the information
    formation_info = {}

    # Presentation section
    presentation_section = soup.find('h3', string='Présentation de la formation')
    try:
        if presentation_section:
            # Get the text of the next div with the class 'word-break-break-word'
            formation_info['presentation'] = presentation_section.find_next('div',
                                                                            class_='word-break-break-word').get_text()
    except AttributeError:
        pass

    # Inscription section
    frais_section = soup.find('h3', string="Frais de candidature")
    try:
        if frais_section:
            formation_info['frais'] = frais_section.find_previous().get_text()
    except AttributeError:
        pass

    # Study continuation section
    poursuite_section = soup.find('h3', string="Poursuite d'études")
    try:
        if poursuite_section:
            formation_info['poursuite_etu'] = poursuite_section.find_previous().get_text()
    except AttributeError:
        pass

    # Professional opportunities section
    debouche_section = soup.find('h3', string="Débouchés professionnels")
    try:
        if debouche_section:
            formation_info['debouche'] = debouche_section.find_next('div', class_='word-break-break-word').get_text()
    except AttributeError:
        pass

    # Cleanup
    if 'presentation' in formation_info:
        formation_info['presentation'] = ' '.join(formation_info['presentation'].split())
    if 'frais' in formation_info:
        formation_info['frais'] = ' '.join(formation_info['frais'].split())
    if 'poursuite_etu' in formation_info:
        formation_info['poursuite_etu'] = ' '.join(formation_info['poursuite_etu'].split())
    if 'debouche' in formation_info:
        formation_info['debouche'] = ' '.join(formation_info['debouche'].split())

    return formation_info


def convert_dict_to_str(formation_info):
    text = ""

    for key, value in formation_info.items():
        text += f"{key.capitalize()} : {value}\n\n"

    return text
