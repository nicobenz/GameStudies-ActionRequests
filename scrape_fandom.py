import re
import requests
from bs4 import BeautifulSoup
from icecream import ic


def scrape_from_quest(quest_url):
    # url of the quest

    # get pages source
    response = requests.get(quest_url)

    # find all spans of class mw-headline
    pattern = r'<span class="mw-headline" id="Objectives">Objectives<\/span>(.*?)<h2'

    # Use re.findall() to find all matches of the pattern in the HTML content
    matches = re.findall(pattern, response.text, re.DOTALL)

    # if match, extract the objectives from their lists
    if matches:
        extracted_content = matches[0].strip()
        soup = BeautifulSoup(extracted_content, features="html.parser")
        objectives = soup.find_all("ul")

        objectives = objectives[0].text.split("\n")
    else:
        objectives = []

    # get game and quest name from url
    game_name = url.split("//")[1].split(".")[0]
    quest_name = url.split("/")[-1]

    # collect data in a dict to save in json later
    save_dict = {
        "game": game_name,
        "quest": quest_name,
        "objectives": objectives
    }
    return save_dict


url = "https://cyberpunk.fandom.com/wiki/Love_Like_Fire"

objectives = scrape_from_quest(url)
