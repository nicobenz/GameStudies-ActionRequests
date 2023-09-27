import os
import shutil
import random

target_directory = "/Volumes/Data/transcripts"

# get subdirs
subdirectories = [f.path for f in os.scandir(target_directory) if f.is_dir()]

# flatten
for subdirectory in subdirectories:
    # get all files
    files = [f.path for f in os.scandir(subdirectory) if f.is_file() and ".DS_Store" not in f.name]

    # move file
    for file in files:
        # handle exception caused by identical file names
        try:
            shutil.move(file, target_directory)
        except shutil.Error as e:
            random_suffix = random.randint(111, 999)
            base_name = os.path.basename(file)
            new_name = os.path.splitext(base_name)[0] + f"_{random_suffix}" + os.path.splitext(base_name)[1]
            new_path = os.path.join(target_directory, new_name)
            shutil.move(file, new_path)

    # remove folder
    os.rmdir(subdirectory)