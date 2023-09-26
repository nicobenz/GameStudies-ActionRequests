import whisper
from whisper.utils import get_writer
import os
import time
from pydub import AudioSegment


def format_time(seconds):
    hours, rest = divmod(int(seconds), 3600)
    minutes, seconds = divmod(rest, 60)
    if seconds > 30:
        minutes += 1
    return f"{hours:02d}:{minutes:02d}"


# load audio files
source_path = "data/audio"
audio_files = [file for file in os.listdir(source_path) if ".DS_Store" not in file]
audio_files.sort()

# set whisper model
model = whisper.load_model("base")

# transcribe all audio files
for audio_file in audio_files:
    file = f"{source_path}/{audio_file}"
    # load into pydub to calculate length
    audio_object = AudioSegment.from_file(file)
    audio_length = len(audio_object)  # in milliseconds
    audio_length = int(audio_length / 1000.0)  # to seconds
    # measure start time
    start_time = time.time()
    # transcribe
    result = model.transcribe(file, language="en", fp16=False, verbose=False)
    # measure end time
    end_time = time.time()
    # save using text writer to get chunked output instead of one line (needed to deal with hallucinations easier)
    output_directory = "data/transcripts_yt/raw"
    word_options = {}  # empty to not mess with whispers segmentation
    txt_writer = get_writer("txt", output_directory)
    txt_writer(result, audio_file, word_options)  # has a warning of wrong input (str instead of TextIO) but works fine
    # calculate time for informative output
    raw_sec = end_time - start_time
    percentage = round((raw_sec / audio_length) * 100, 2)
    file_duration = format_time(audio_length)
    trans_duration = format_time(raw_sec)

    print(f"Finished: {audio_file.split('/')[-1]}")
    print(f"- File duration:               {file_duration}")
    print(f"- Transcription duration:      {trans_duration}")
    print(f"- Percentage of file duration: {percentage}%")
