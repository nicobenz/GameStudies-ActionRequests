from pytube import Channel
from tqdm import tqdm
import re
import shutil
import os

"""
pytube is currently broken because of new youtube channel url types that need new regex patterns.
manually merging fix from https://github.com/pytube/pytube/pull/1658 in local files worked though
"""


def download_videos(channels):
    # loop over all youtube channels
    count = 1
    for idx, chan in enumerate(channels):
        # set channel
        c = Channel(chan)

        # set save directories
        temp_path = "temp"
        save_path = "data/audio"

        # set priority list of file types because youtube videos dont always have a certain file format
        audio_formats = ["wav", "mp3", "m4a", "mp4", "mpeg", "mpga", "webm"]
        audio_format = ""  # to suppress warning later
        saved_videos = []

        # get video number for tqdm process bar
        num_videos = len(c.video_urls)

        # loop over all videos of the channel
        for jdx, video in tqdm(enumerate(c.videos, start=count), total=num_videos):
            count += 1  # increment count for continuous numbering of audio files across all channels
            selected_audio_stream = None
            audio_stream = None
            # only use videos with the keywords in title and without mod in title
            if (all(keyword in video.title.lower() for keyword in ["no commentary", "full game", "gameplay"])
                    and " mod " or " mod)" not in video.title.lower()):
                # shape title to fitting save name
                game_name = video.title.split(" | ")[0]
                game_name = game_name.strip().lower().split(" ")
                game_name = '_'.join(game_name)
                game_name = game_name.replace("&", "and")
                game_name = re.sub(r'[^a-zA-Z0-9_]', '', game_name)
                save_name = f"{jdx:03d}_{game_name}"
                # only use games that are not already saved
                if game_name not in saved_videos:
                    # loop through all audio formats until hit, then leave loop
                    for audio_format in audio_formats:
                        audio_stream = video.streams.filter(only_audio=True, file_extension=audio_format).first()
                        if audio_stream:
                            selected_audio_stream = audio_stream
                            break
                # if audio stream selected, save
                if selected_audio_stream:
                    saved_videos.append(game_name)
                    audio_stream.download(output_path=f"{temp_path}/{save_name}")
                    saved_file = os.listdir(f"{temp_path}/{save_name}")[0]
                    shutil.move(f"{temp_path}/{save_name}/{saved_file}", f"{save_path}/{save_name}.{audio_format}")
                    shutil.rmtree(f"{temp_path}/{save_name}")
