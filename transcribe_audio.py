import shutil
from tqdm import tqdm
import whisper
from whisper.utils import get_writer
import os
import time
from pydub import AudioSegment
import numpy as np
from scipy.signal import lfilter
import subprocess


def format_time(seconds):
    hours, rest = divmod(int(seconds), 3600)
    minutes, seconds = divmod(rest, 60)
    if seconds > 30:
        minutes += 1
    return f"{hours}:{minutes:02d}"


def calculate_total_audio_length(folder_path):
    total_length = 0

    # Iterate through all files in the folder
    for filename in tqdm(os.listdir(folder_path)):
        if filename.endswith('.m4a'):
            # Run FFmpeg command to get audio duration
            command = ['ffprobe', '-i', os.path.join(folder_path, filename), '-show_entries', 'format=duration', '-v',
                       'quiet', '-of', 'csv=p=0']
            audio_length = float(subprocess.check_output(command))
            total_length += audio_length

    return format_time(int(total_length))


def transcribe(audio_files: list, model_size="base"):
    model_sizes = ["tiny", "base", "small", "medium"]
    # set whisper model
    if model_size in model_sizes:
        model = whisper.load_model(f"{model_size}.en")
    else:
        raise ValueError("Incorrect model size specified. Use 'tiny', 'base', 'small' or 'medium'.")

    # transcribe all audio files
    for audio_file in audio_files:
        file = audio_file.split("/")[-1]
        # preprocess with noise reduction and high pass filters

        # load into pydub to calculate length
        audio_object = AudioSegment.from_file(audio_file)
        audio_length = len(audio_object)  # in milliseconds
        audio_length = int(audio_length / 1000.0)  # to seconds
        # measure start time
        start_time = time.time()
        # transcribe
        result = model.transcribe(audio_file, language="en", fp16=False, verbose=False)
        # measure end time
        end_time = time.time()
        # save using text writer to get chunked output instead of one line (needed to deal with hallucinations easier)
        output_directory = "data/transcripts_yt/raw"
        word_options = {}  # empty to not mess with whispers segmentation
        txt_writer = get_writer("txt", output_directory)
        txt_writer(result, file, word_options)  # has a warning of wrong input (needs TextIO) but works fine
        # calculate time for informative output
        raw_sec = end_time - start_time
        percentage = round((raw_sec / audio_length) * 100, 2)
        file_duration = format_time(audio_length)
        trans_duration = format_time(raw_sec)
        file = file.split(".")[0]
        shutil.move(f"{output_directory}/{file}.txt", f"{output_directory}/{file}_{model_size}.txt")

        print(f"Finished: {audio_file.split('/')[-1]}")
        print(f"- File duration:               {file_duration}")
        print(f"- Transcription duration:      {trans_duration}")
        print(f"- Percentage of file duration: {percentage}%")


def preprocess_audio(audio_files, save_sample=False):
    for audio_file in audio_files:
        audio = AudioSegment.from_file(audio_file)
        audio_array = np.array(audio.get_array_of_samples())

        coef = 0.97
        a = [1]
        b = [1, -coef]
        processed_audio = lfilter(b, a, audio_array)

        # back to audio segment
        processed_audio = AudioSegment(
            processed_audio.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=1
        )

        if save_sample:
            start = 5
            end = 10

            # extract sample
            sample = processed_audio[start*1000:end*1000]

            # save
            save_path = "temp/audio_check.wav"
            sample.export(save_path, format="wav")

        save_name = audio_file.split("/")[-1]
        save_name = save_name.split(".")[0] + ".wav"
        processed_audio.export(f"data/audio/processed/{save_name}", format="wav")


# load audio files
source = "/Volumes/Data/transcripts/valid"
audios = [f"{source}/{file}" for file in os.listdir(source) if ".DS_Store" not in file]
audios.sort()

# preprocess all audios
#preprocess_audio(audios, save_sample=True)

# transcribe
#models = ["tiny", "base", "small", "medium"]
#for model_size in models:
#    transcribe(audios, model_size=model_size)
audio_len = calculate_total_audio_length(source)
print(audio_len)
