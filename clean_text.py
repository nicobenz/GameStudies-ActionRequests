import os
import re
import spacy
from tqdm import tqdm

whitelist = []

all_transcripts = [file for file in os.listdir("data/transcripts/raw") if ".DS_Store" not in file]
all_transcripts.sort()

nlp = spacy.load("en_core_web_sm")
with open("data/custom_stopwords.text", "r") as f:
    custom_stops = f.read()
custom_stops = custom_stops.split("\n")
custom_stops = [stop for stop in custom_stops if stop != ""]

for transcript in tqdm(all_transcripts):
    with open(f"data/transcripts/raw/{transcript}") as f:
        content = f.read()

    script = content.replace('\n', ' ')
    script = re.sub(r'\s+', ' ', script)
    doc = nlp(script)
    filtered_tokens = [
        tok.lemma_.lower()
        for tok in doc
        if not (tok.is_stop and tok.lemma_.lower() not in whitelist or tok.ent_type_ or not tok.is_alpha) and tok.lemma_.lower() not in custom_stops]
    filtered_tokens = ' '.join(filtered_tokens)

    with open(f"data/transcripts/clean/{transcript}", "w") as f:
        f.write(filtered_tokens)
