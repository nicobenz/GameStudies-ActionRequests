import os
import shutil
import re


def create_file_name(file_name: str):
    file_name = file.split(" _ ")[0]
    file_name = file_name.replace("&", "and")
    file_name = file_name.replace("_", "")
    file_name = file_name.replace(".", "")
    file_name = file_name.replace("'", "")
    file_name = file_name.replace(" - ", " ")
    file_name = file_name.split(" ")
    file_name = [tok.lower() for tok in file_name]
    file_name = '_'.join(file_name)
    return file_name


valid_dir = "/Volumes/Data/transcripts/valid"
nope_dir = "/Volumes/Data/transcripts/nope"

files = [f for f in os.listdir(valid_dir) if ".DS_Store" not in f]
files.sort()

transcript_dir = "/Users/nico/code/GameStudies-TopicCurves/data/transcripts/clean"
current_transcripts = [f for f in os.listdir(transcript_dir) if ".DS_Store" not in f]
current_transcripts.sort()

pattern = r"^[0-9]{4}_"

num = int(current_transcripts[-1].split("_")[0])+1
for file in files:
    if not re.match(pattern, file):
        if all(keyword in file.lower() for keyword in ["no commentary", "full game", "gameplay"]):
            audio_format = file.split(".")[-1]
            save_name = create_file_name(file)
            current_num = f"{num:04d}"
            save_name = '_'.join([current_num, save_name])
            num += 1
            shutil.move(f"{valid_dir}/{file}", f"{valid_dir}/{save_name}.{audio_format}")
        else:
            shutil.move(f"{valid_dir}/{file}", f"{nope_dir}/{file}")

# reorder all files
num = int(current_transcripts[-1].split("_")[0])+1
files = [f for f in os.listdir(valid_dir) if ".DS_Store" not in f]
files.sort()

for file in files:
    new_name = file[4:]
    new_name = f"{num:04d}{new_name}"

    old = os.path.join(valid_dir, file)
    new = os.path.join(valid_dir, new_name)

    os.rename(old, new)
    num += 1
