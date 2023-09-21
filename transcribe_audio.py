import whisper
import os

# load audio files
source_path = "data/audio"
audio_files = [file for file in os.listdir(source_path) if ".DS_Store" not in file]

# set whisper model
model = whisper.load_model("base")

# transcribe all audio files
for audio_file in audio_files:
    # transcribe
    result = model.transcribe(f"{source_path}/{audio_file}", language="en", fp16=False, verbose=False)
    # save
    with open(f"data/transcripts_yt/{audio_file.split('.')[0]}.txt", "w", encoding="utf-8") as f:
        f.write(result["text"])
