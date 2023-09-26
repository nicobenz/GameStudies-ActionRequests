import os
import re
import spacy
from tqdm import tqdm


def clean_transcripts(transcript_path):
    # list of tokens that should not be filtered by spacys stopword filter
    whitelist = []

    # get all transcript files and sort
    all_transcripts = [file for file in os.listdir(transcript_path) if ".DS_Store" not in file]
    all_transcripts.sort()

    # load spacy model and custom stopwords
    nlp = spacy.load("en_core_web_sm")
    with open("data/custom_stopwords.text", "r") as f:
        custom_stops = f.read()
    custom_stops = custom_stops.split("\n")
    custom_stops = [stop for stop in custom_stops if stop != ""]

    all_verbs = set()
    # loop through all transcripts
    for transcript in tqdm(all_transcripts):
        with open(f"{transcript_path}/{transcript}") as f:
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


def prepare_whisper_transcripts(transcript_path):
    # get all transcript files and sort
    all_transcripts = [file for file in os.listdir(transcript_path) if ".DS_Store" not in file]
    all_transcripts.sort()

    for transcript in all_transcripts:
        file = f"{transcript_path}/{transcript}"
        with open(file, "r") as f:
            content = f.read()
        content = content.split("\n")
        segments_to_remove = []
        for idx, segment in enumerate(content):
            if idx > 0:
                last_segment = content[idx-1]
                if last_segment == segment:
                    segments_to_remove.append(idx)
        clean_content = [content[i] for i in range(len(content)) if i not in segments_to_remove]

        # save
        with open(f"data/transcripts_yt/prepared/{transcript}", "w", encoding="utf8") as f:
            for line in clean_content:
                f.write(f"{line}\n")


clean_transcripts("data/transcripts/raw")
prepare_whisper_transcripts("data/transcripts_yt/raw")
clean_transcripts("data/transcripts_yt/prepared")
