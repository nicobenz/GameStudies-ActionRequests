import json
import os
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from icecream import ic
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
from collections import Counter



def scrape_from_quest(quest_data):
    # get pages source
    response = requests.get(quest_data[0])
    # get everything that is between class mw-headline with id objectives and the next h2 or the start of the navbox
    pattern = (r'<span class="mw-headline" id="Objectives">Objectives<\/span>(.*?)'
               r'(?:<h2>|<table class="navbox mw-collapsible")')

    # Use re.findall() to find all matches of the pattern in the HTML content
    matches = re.findall(pattern, response.text, re.DOTALL)
    # if match, extract the objectives from their lists
    objectives_found = []
    if not matches:
        pattern = r'<aside role="region" class="portable-infobox(.*?)</aside>'
        matches = re.findall(pattern, response.text, re.DOTALL)
    if matches:
        extracted_content = matches[0].strip()
        soup = BeautifulSoup(extracted_content, features="html.parser")
        quest_objectives = soup.find_all("ul")
        if not quest_objectives:
            quest_objectives = soup.find_all("ol")
        if quest_objectives:
            for quest_objective in quest_objectives:
                soup = BeautifulSoup(str(quest_objective), 'html.parser')
                li_tags = soup.find_all('li')
                for li in li_tags:
                    objectives_found.append(li.get_text())

    # collect data in a dict to save in json later
    save_dict = {
        "quest name": quest_data[1],
        "objectives": objectives_found
    }
    return save_dict


def get_quest_urls(wiki_url):
    # extract the urls of all quests from the games wiki
    pattern = r'<a href="/wiki/(.*?)" title="(.*?)">(.*?)</a>'
    results = []
    length_threshold = 50
    url_base = wiki_url[0].split("wiki")[0]

    for url in wiki_url:
        response = requests.get(url)
        matches = re.findall(pattern, response.text, re.DOTALL)

        for match in matches:
            if len(match[0]) < length_threshold and len(match[2]) < length_threshold:
                results.append((url_base + "wiki/" + match[0], match[2]))

    return results


def plot_treemap():
    """
    explorative plotting of treemap for each game
    :return: no return
    """
    files = [file for file in os.listdir("data/objectives") if ".DS_Store" not in file]

    for file in files:
        game = file.split(".")[0]
        game = game.lower()  # name for saving file
        if " " in game:
            game = '_'.join(game.split(" "))
        games_verbs = []
        with open(f"data/objectives/{file}") as f:
            content = json.load(f)
        for quest in content:
            # extract the first word of each objective (the imperative verb)
            for objective in quest["objectives"]:
                objective_list = objective.split(" ")
                if objective_list[0] != "If":
                    games_verbs.append(objective_list[0])

        verb_counts = Counter(games_verbs)  # count unique occurrences

        # put verb counts in a dict, sort them descending and limit to first 15 verbs
        data = dict(verb_counts)
        data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
        data = dict(list(data.items())[:15])

        # calculate percentages for plot
        total = sum(data.values())
        percentages = [(count / total) * 100 for count in data.values()]

        # rectangle style plot dimensions
        plt.subplots(figsize=(8, 4))

        # plot using squarify
        squarify.plot(
            sizes=percentages,
            label=[f'{key}\n{round(val, 1)}%' for key, val in zip(data.keys(), percentages)],  # zip labels and percent
            alpha=0.7,
            color=sns.color_palette('deep', n_colors=len(data))
        )
        # plot needs no axis
        plt.axis('off')
        plt.title(file.split(".")[0], fontsize=16)
        # save as pdf and png
        plt.savefig(f"data/results/plots/treemap_{game}.pdf")
        plt.savefig(f"data/results/plots/treemap_{game}.png", dpi=300)


# find a way to get these quest urls for every game from fandom
games = [
    {
        "name": "Cyberpunk 2077",
        "urls": [
            "https://cyberpunk.fandom.com/wiki/Cyberpunk_2077_Main_Jobs",
            "https://cyberpunk.fandom.com/wiki/Cyberpunk_2077_Side_Jobs",
            "https://cyberpunk.fandom.com/wiki/Cyberpunk_2077_Gigs"
        ]
    },
    {
        "name": "Horizon Zero Dawn",
        "urls": [
            "https://horizon.fandom.com/wiki/Horizon_Zero_Dawn_quests"
        ]
    },
    {
        "name": "Horizon Forbidden West",
        "urls": [
            "https://horizon.fandom.com/wiki/Horizon_Forbidden_West_quests"
        ]
    },
    {
        "name": "The Witcher 1",
        "urls": [
            "https://witcher.fandom.com/wiki/The_Witcher_quests"
        ]
    },
    {
        "name": "The Witcher 2",
        "urls": [
            "https://witcher.fandom.com/wiki/The_Witcher_2_quests"
        ]
    },
    {
        "name": "The Witcher 3",
        "urls": [
            "https://witcher.fandom.com/wiki/The_Witcher_3_main_quests",
            "https://witcher.fandom.com/wiki/The_Witcher_3_secondary_quests",
            "https://witcher.fandom.com/wiki/The_Witcher_3_contracts",
            "https://witcher.fandom.com/wiki/The_Witcher_3_treasure_hunts",
            "https://witcher.fandom.com/wiki/Hearts_of_Stone_quests",
            "https://witcher.fandom.com/wiki/Blood_and_Wine_quests"
        ]
    },
    {
        "name": "Thronebreaker",
        "urls": [
            "https://witcher.fandom.com/wiki/Thronebreaker:_The_Witcher_Tales"
        ]
    },
    {
        "name": "Hogwarts Legacy",
        "urls": [
            "https://hogwarts-legacy.fandom.com/wiki/Quests"
        ]
    },
    {
        "name": "Diablo I",
        "urls": [
            "https://diablo.fandom.com/wiki/Diablo_I_Quests",
            "https://diablo.fandom.com/wiki/Hellfire_quests"
        ]
    },
    {
        "name": "Diablo II",
        "urls": [
            "https://diablo.fandom.com/wiki/Diablo_II_quests"
        ]
    },
    {
        "name": "Diablo III",
        "urls": [
            "https://diablo.fandom.com/wiki/Diablo_III_Quests"
        ]
    },
    {
        "name": "Diablo IV",
        "urls": [
            "https://diablo.fandom.com/wiki/Diablo_IV_Campaign_Quests",
            "https://diablo.fandom.com/wiki/Diablo_IV_Priority_Quests",
            "https://diablo.fandom.com/wiki/Diablo_IV_Seasonal_Quests",
            "https://diablo.fandom.com/wiki/Diablo_IV_Side_Quests"
        ]
    }
]
"""
# make progress bar pretty
game_names = [game["name"] for game in games]
longest_name = max(len(s) for s in game_names)
formated_bar = "{desc} {percentage:3.0f}%|{bar}{r_bar}"
current_files = [file for file in os.listdir("data/objectives") if ".DS_Store" not in file]
for game in games:
    if game["name"] not in current_files:
        progress_descr = game["name"].ljust(longest_name)
        quests = get_quest_urls(game["urls"])
        objectives_collection = []
        for quest in tqdm(quests, desc=progress_descr, bar_format=formated_bar):
            objectives = scrape_from_quest(quest)
            if objectives["objectives"]:
                objectives_collection.append(objectives)
        if objectives_collection:  # only save json if objectives found
            with open(f"data/objectives/{game['name']}.json", "w") as f:
                json.dump(objectives_collection, f)

"""

# WIP: Starcraft II
test_dict = scrape_from_quest(("https://starcraft.fandom.com/wiki/The_Great_Train_Robbery", "The Great Train Robbery"))
ic(test_dict)
plot_treemap()
