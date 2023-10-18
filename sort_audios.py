import os
import shutil
import re


def filter_string(input_string):
    filter_token = [
        "(192kbitaac)m4a",
        "no_commentary",
        "[1080p_hd_60fps_pc]",
        "[4k_60fps]",
        "[4k_60fps_pc_ultra]",
        "full_gameplay_walkthrough",
        "full_game",
        "gameplay",
        "()",
        "(4k_60fps)",
        "ps5_game",
        "in_4k",
        "[1080p_hd_xbox_one_x]",
        "(128kbitaac)m4a",
        "[1080p_hd_ps4]",
        "[4k_60fps_pc]",
        "[1080p_hd_pc]",
        "[1080p_hd_60fps]",
        "4k_60fps",
        "[1080p_60fps_pc]",
        "[1440p_60fps_pc]",
        "[1080p_hd_60fps_ps4_pro]",
        "100%",
        "[_ps5]",
        "(_)",
        "[4k_ultra_hd]",
        "_game_",
        "(__ultra)",
        "[1440p_hd_60fps_pc]",
        "ultra_hd",
        "ps5",
        "[_ultra]",
        "[4k_hd]",
        "[_pc_rtx_3090]",
        "(4k_)",
        "ps4_pro",
        "(_rtx)ultra_pc",
        "4k",
        "[xbox_one]",
        "1080p_hd",
        "[_]",
        "60fps",
        "[_pc_rtx]",
        "[1080p__]",
        "[1440p__]",
        "[_xbox_series_x]",
        "[__pc_max_settings]",
        "[__pc_ultra]",
        "[_xbox_one]",
        "[_pc_ultra_settings]",
        "(_ray_tracing)",
        "[pc_ultra]",
        "[_pc_ultra]",
        "[_pc_ultra_rtx]",
        "[_pc_ultra_ray_tracing]",
        "[_ray_tracing_pc]",
        "(_ultra)",
        "[]",
        "(hd)",
        "[1080p__pc_ultra]",
        "[1440p_hd_]",
        "_hd_",
        "full_walkthrough",
        "[__ray_tracing]",
        "[_ultra_rtx_3090]",
        "【】",
        "_uhd_",
        "(__)",
        "(_rtx)",
        "ultra_realistic_graphics",
        "[_ray_tracing]",
        "[1080p__vr_valve_index]",
        "pc____ultrahd",
        "(_psvr2)",
        "[_psvr_2]",
        "pc_",
        "ray_tracing",
        "[1440p_]",
        "[_pc]",
        "(ps4xb1pc)",
        "1440p",
        "[_max_settings]",
        "[ps4]",
        "(1080p__)",
        "[_ultra_pc]",
        "[_ps_now_]",
        "[_ps2]",
        "1080p",
        "xbox_series_x",
        "(__pc)",
        "(8k_)",
        "(xboxswitch)",
        "vr_",
        "(_hdr)",
        "_【",
        "ps4",
        "(_max_settings)",
        "[__hd]",
        "[_vr]",
        "[_rtx]",
        "(pc)",
        "[__]",
        "(_pc)"
        ",",
        "[__nvidia_rtx]",
        "[_nvidia_rtx]",
        "[__xbox_one]",
        "no_hud_immersion",
        "】"
    ]
    for f in filter_token:
        input_string = input_string.replace(f, "")

    input_string = input_string.replace("____", "_")
    input_string = input_string.replace("___", "_")
    input_string = input_string.replace("__", "_")

    input_string = input_string.replace("_–_", "_")
    input_string = input_string.replace("_––_", "_")
    input_string = input_string.replace(",_", "_")

    input_string = input_string.split(".")
    input_string[0] = input_string[0].rstrip("_")
    input_string = ".".join(input_string)

    return input_string


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


new_dir = "/Volumes/Data/transcripts/new"
valid_dir = "/Volumes/Data/transcripts/valid"
nope_dir = "/Volumes/Data/transcripts/nope"

files = [f for f in os.listdir(new_dir) if ".DS_Store" not in f]
files.sort()

current_transcripts = [f for f in os.listdir(valid_dir) if ".DS_Store" not in f]
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
            shutil.move(f"{new_dir}/{file}", f"{valid_dir}/{save_name}.{audio_format}")
        else:
            shutil.move(f"{valid_dir}/{file}", f"{nope_dir}/{file}")

# reorder all files
num = 1
files = [f for f in os.listdir(valid_dir) if ".DS_Store" not in f]
files.sort()

for file in files:
    new_name = file[4:]
    # filter some stuff
    new_name = filter_string(new_name)
    new_name = f"{num:04d}{new_name}"

    old = os.path.join(valid_dir, file)
    new = os.path.join(valid_dir, new_name)

    os.rename(old, new)
    num += 1
