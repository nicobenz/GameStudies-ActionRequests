import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import os
import json
import spacy
import numpy as np
from sklearn.cluster import SpectralClustering


def main():
    # get_quest_data(verbose=True)
    # process_quest_data()
    # time.sleep(5)
    # prune_verbs()
    # time.sleep(5)
    # cluster_verbs()
    # time.sleep(5)
    expand_verbs()


def get_quests_from_categories():
    def has_next_page(tag):
        return tag.name == "a" and tag.text.strip() == "next page"

    with open("data/wow/quest_category_urls.txt") as f:
        urls = f.readlines()

    urls = [url.strip() for url in urls]

    base_url = "https://wowpedia.fandom.com"

    quest_urls = []
    for url in tqdm(urls):
        while True:
            time.sleep(1)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, features="html.parser")

            page_div = soup.find("div", class_="mw-category-generated")
            quest_div = page_div.find("div", class_="mw-content-ltr")

            quests = quest_div.find_all("a")
            for quest in quests:
                quest_urls.append(base_url + quest["href"])

            next_page = page_div.find(has_next_page)

            if next_page:
                url = base_url + next_page["href"]
            else:
                break

    with open("data/wow/quest_urls.txt", "w") as f:
        for url in quest_urls:
            f.write(url + "\n")


def filter_quests():
    with open("data/wow/quest_urls.txt") as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    filtered_urls = []
    for url in urls:
        if "_(Horde)" not in url and "_(Alliance)" not in url:
            horde_version = url + "_(Horde)"
            alliance_version = url + "_(Alliance)"
            if horde_version in urls and alliance_version in urls:
                pass
            else:
                filtered_urls.append(url)
        else:
            filtered_urls.append(url)

    with open("data/wow/filtered_quest_urls.txt", "w") as f:
        for url in filtered_urls:
            f.write(url + "\n")


def save_html_source():
    def get_with_retry(url, max_retries=5, backoff_factor=1):
        for retry in range(max_retries):
            url_response = requests.get(url)
            if url_response.status_code != 429:  # If not 'Too Many Requests'
                return url_response
            else:
                wait_time = backoff_factor * (2 ** retry)
                time.sleep(wait_time)
        raise Exception(f"Failed to get a successful response after {max_retries} attempts.")

    with open("data/wow/quest_urls.txt") as f:
        urls = f.readlines()

    urls = [url.strip() for url in urls]

    for i, url in tqdm(enumerate(urls), total=len(urls)):
        start_time = time.time()

        response = get_with_retry(url)
        with open(f"data/wow/quest_html/{i}.html", "w") as f:
            f.write(response.text)

        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time < 1:
            time.sleep(1.2 - elapsed_time)


def get_quest_data(verbose=True):
    """
    Extracts quest data from the html files.
    """
    def find_th(tag_string, target):
        return tag_string.name == 'th' and tag_string.string == target
    quest_path = "data/wow/quest_html"
    urls = [os.path.join(quest_path, url) for url in os.listdir(quest_path) if url.endswith(".html")]

    contents = []
    for url in tqdm(urls, disable=not verbose):
        quest_content = {}
        with open(url) as f:
            content = f.read()

        soup = BeautifulSoup(content, features="html.parser")

        quest_id = soup.find("li", class_="wowhead")
        if quest_id:
            quest_id = quest_id.find("a")
            if quest_id:
                quest_id = quest_id["href"].split("=")[-1]
                if quest_id.isdigit():
                    quest_content["id"] = quest_id
                else:
                    quest_content["id"] = None
            else:
                quest_content["id"] = None
        else:
            quest_content["id"] = None
        quest_url = soup.find("meta", property="og:url")

        if quest_url:
            quest_url = quest_url.get("content", None)
            if not quest_url:
                continue
            else:
                quest_content["url"] = quest_url
        else:
            continue

        objective = soup.find("span", class_="mw-headline", id="Objectives")
        if not objective:
            continue

        header = objective.find_parent("h2")

        objectives = []
        for item in header.next_siblings:
            if "<h2>" in str(item):
                break
            objective_text = item.text.strip()
            if objective_text:
                objectives.append(objective_text)
        quest_content["objectives"] = objectives

        patch_changes = soup.find("span", class_="mw-headline", id="Patch_changes")
        patch_number = None
        if patch_changes:
            header = patch_changes.find_parent("h2")

            for item in header.next_siblings:
                if "<h2>" in str(item):
                    break
                ul_element = BeautifulSoup(str(item), features="html.parser")
                li_elements = ul_element.find_all('li')
                if li_elements:
                    last_li = li_elements[-1]
                    patch_tag = last_li.find('b')
                    if patch_tag:
                        patch_number = patch_tag.get_text().split(':')[0]
                        patch_number = patch_number.split(' ')[1]

        quest_content["patch"] = patch_number

        info_table = soup.find("table", class_="infobox darktable questbox")

        if info_table:
            titles = ["Alliance", "Horde", "Neutral", "Alliance & Horde"]
            for title in titles:
                faction = info_table.find("a", title=title)
                if faction:
                    quest_content["faction"] = faction["title"]
                    break
            else:
                quest_content["faction"] = None

            infobox_items = ["Level", "Category", "Previous", "Next"]
            for item in infobox_items:
                label = info_table.find(lambda tag: find_th(tag, item))
                if label:
                    sibling = label.find_next_sibling("td")
                    if sibling:
                        target_text = sibling.text.strip()
                        if "\xa0" in target_text:
                            target_text = target_text.split("\xa0")[-1].strip()
                        quest_content[item.lower()] = target_text
                    else:
                        quest_content[item.lower()] = None

            title = soup.find("meta", property="og:title")
            if title:
                quest_content["title"] = title["content"]
            else:
                quest_content["title"] = None
        contents.append(quest_content)

    with open("data/wow/quest_data.txt", "w") as f:
        json.dump(contents, f, indent=4)


def process_quest_data():
    with open("data/wow/quest_data.txt") as f:
        quests = json.load(f)

    filtered_quests = []
    for quest in tqdm(quests, desc="Filtering quests"):
        full_quest = True
        for q_key, q_val in quest.items():
            if not q_val:
                full_quest = False
        if full_quest:
            filtered_quests.append(quest)

    nlp = spacy.load("en_core_web_md")
    for quest in tqdm(filtered_quests, desc="Updating quests"):
        objectives = quest["objectives"]

        updated_objectives = []

        split_objectives = []
        for objective in objectives:
            split_obj = objective.split("\n")
            for obj in split_obj:
                split_objectives.append(obj)
        for objective in split_objectives:
            if "\xa0" not in objective:
                if objective and objective[0] != "[" and objective[-1] != ")" and objective[-1] != "]" and objective != "OR":
                    updated_objectives.append(objective)
        quest["objectives"] = updated_objectives
    directive_verbs = ["want", "ask", "tell", "need", "require", "order", "urge"]
    extracted_verbs = []
    for quest in tqdm(filtered_quests, desc="Processing quests"):
        for objective in quest["objectives"]:
            doc = nlp(objective)
            for sent in doc.sents:
                if sent[0].pos_ == "VERB":
                    patch = quest.get("patch", None)
                    if patch:
                        patch = patch.split(".")[0]

                    level = quest.get("level", None)
                    if level:
                        if "\u2002" in level:
                            level = level.split("\u2002")[0]

                    verb_data = {
                        "verb": sent[0].lemma_.lower(),
                        "patch": patch,
                        "faction": quest.get("faction", None),
                        "level": level,
                        "category": quest.get("category", None),
                        "type": "imperative"
                    }
                    extracted_verbs.append(verb_data)
                else:
                    if sent.root.pos_ == "VERB" and sent.root.lemma_ in directive_verbs:
                        if len(sent) > (sent.root.i + 1):
                            has_comp = [tok for tok in sent if tok.dep_ == "xcomp" or tok.dep_ == "ccomp"]
                            if has_comp:
                                patch = quest.get("patch", None)
                                if patch:
                                    patch = patch.split(".")[0]

                                level = quest.get("level", None)
                                if level:
                                    if "\u2002" in level:
                                        level = level.split("\u2002")[0]

                                verb_data = {
                                    "verb": has_comp[0].lemma_.lower(),
                                    "patch": patch,
                                    "faction": quest.get("faction", None),
                                    "level": level,
                                    "category": quest.get("category", None),
                                    "type": "complement"
                                }
                                extracted_verbs.append(verb_data)

    filtered_verbs = []
    for verb in tqdm(extracted_verbs, desc="Filtering quests"):
        full_verb = True
        for q_key, q_val in verb.items():
            if not q_val:
                full_verb = False
        if full_verb:
            filtered_verbs.append(verb)

    with open("data/wow/verb_data.json", "w") as f:
        json.dump(filtered_verbs, f, indent=4)


def prune_verbs():
    with open("data/wow/verb_data.json") as f:
        verb_data = json.load(f)

    verbs = [verb["verb"] for verb in verb_data]

    verb_counts = {}
    for verb in verbs:
        if verb in verb_counts:
            verb_counts[verb] += 1
        else:
            verb_counts[verb] = 1

    sorted_verb_counts = sorted(verb_counts.items(), key=lambda x: x[1], reverse=True)

    labels, counts = zip(*sorted_verb_counts)

    accepted_labels = []
    manual_remove = ["darkwe"]
    for label, count in zip(labels, counts):
        if count >= 10 and label not in manual_remove:
            accepted_labels.append(label)

    pruned_data = []
    for verb in verb_data:
        if verb["verb"] in accepted_labels:
            pruned_data.append(verb)

    with open("data/wow/pruned_verb_data.json", "w") as f:
        json.dump(pruned_data, f, indent=4)


def cluster_verbs():
    def spectral_clustering(vectors, k=5):
        spectral = SpectralClustering(n_clusters=k, random_state=42, affinity='nearest_neighbors', n_init=10)
        clusters = spectral.fit_predict(vectors)

        cluster_dict = {i: [] for i in range(k)}
        for verb, cluster_label in zip(verbs, clusters):
            cluster_dict[cluster_label].append(verb)

        return clusters
    with open("data/wow/pruned_verb_data.json") as f:
        verb_data = json.load(f)
    with open("data/wow/cluster_mapping.json") as f:
        cluster_mapping = json.load(f)

    nlp = spacy.load("en_core_web_md")

    verbs = [verb["verb"] for verb in verb_data]
    seen = set()
    unique_verbs = [x for x in verbs if not (x in seen or seen.add(x))]

    verb_vectors = np.array([nlp(verb).vector for verb in unique_verbs])

    clustering_results = spectral_clustering(verb_vectors)

    labeled_clusters = []
    for cluster_index in clustering_results:
        label = cluster_mapping[str(cluster_index)]
        labeled_clusters.append(label)

    for unique_verb, cluster in zip(unique_verbs, labeled_clusters):
        for verb in verb_data:
            if verb["verb"] == unique_verb:
                verb["cluster"] = cluster

    with open("data/wow/clustered_verbs.json", 'w') as f:
        json.dump(verb_data, f, indent=4)


def expand_verbs():
    with open("data/wow/clustered_verbs.json") as f:
        verb_data = json.load(f)

    expanded_verbs = []
    for verb in tqdm(verb_data, desc="Expanding verbs"):
        level = verb["level"]
        if "-" in level:
            levels = level.split("-")
            levels = range(int(levels[0]), int(levels[1]) + 1)
        else:
            levels = [int(level)]
        for level in levels:
            verb_copy = verb.copy()
            verb_copy["level"] = level
            expanded_verbs.append(verb_copy)
    with open("data/wow/expanded_verb_data.json", "w") as f:
        json.dump(expanded_verbs, f, indent=4)


main()
