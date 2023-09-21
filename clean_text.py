import os
import re
import spacy
from tqdm import tqdm

# list of tokens that should not be filtered by spacys stopword filter
whitelist = []

# get all transcript files and sort
all_transcripts = [file for file in os.listdir("data/transcripts/raw") if ".DS_Store" not in file]
all_transcripts.sort()

nlp = spacy.load("en_core_web_sm")
with open("data/custom_stopwords.text", "r") as f:
    custom_stops = f.read()
custom_stops = custom_stops.split("\n")
custom_stops = [stop for stop in custom_stops if stop != ""]

all_verbs = set()
# loop through all transcripts
for transcript in tqdm(all_transcripts):
    with open(f"data/transcripts/raw/{transcript}") as f:
        content = f.read()
    # remove some stuff
    script = content.replace('\n', ' ')
    script = script.replace('&nbsp;', ' ')
    script = script.replace('--', ' ')
    script = script.replace('/', ' ')
    script = re.sub(r'\s+', ' ', script)
    # load text into spacy model
    doc = nlp(script)
    # filter: only lemmas that are not stopwords and not on whitelist and not a named entity
    filtered_tokens = [
        tok.lemma_.lower()
        for tok in doc
        if not (tok.is_stop and tok.lemma_.lower() not in whitelist or tok.ent_type_) and
        tok.lemma_.lower() not in custom_stops
    ]
    filtered_tokens = ' '.join(filtered_tokens)
    # get all verbs that are not stopwords
    collected_verbs = [
        tok.lemma_.lower()
        for tok in doc
        if not (tok.is_stop and tok.lemma_.lower() not in whitelist or tok.ent_type_) and
        tok.lemma_.lower() not in custom_stops and
        tok.pos_ == "VERB"
    ]
    # add to set
    for verb in collected_verbs:
        all_verbs.add(verb)
    # save
    with open(f"data/transcripts/clean/{transcript}", "w") as f:
        f.write(filtered_tokens)
    with open("data/all_verbs.txt", "w") as f:
        for idx, verb in enumerate(all_verbs):
            if idx < len(all_verbs):
                f.write(f"{verb}\n")
            else:
                f.write(verb)
