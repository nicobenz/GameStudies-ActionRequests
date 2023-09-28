import requests
from bs4 import BeautifulSoup
import json
from pytube import Channel
from tqdm import tqdm


def get_wiki_urls():
    url_collection = []

    page = "https://game-scripts-wiki.blogspot.com"
    first_post = "https://game-scripts-wiki.blogspot.com/2018/06/"
    last_post = "https://game-scripts-wiki.blogspot.com/2023/05/"

    # set start and stop
    start = first_post.split("/")
    current_month = int(start[4])
    current_year = int(start[3])

    end = last_post.split("/")
    max_month = int(end[4])
    max_year = int(end[3])

    # check all posts between start and stop
    while current_month <= max_month or current_year < max_year:
        # build current url
        month = f"{current_month:02d}"
        year = str(current_year)
        combined = '/'.join([year, month])
        url = '/'.join([page, combined, ""])
        content = requests.get(url)
        # read html
        soup = BeautifulSoup(content.text, "html.parser")
        posts = soup.select('script[type="application/ld+json"]')
        # extract target urls
        if posts:
            for post in posts:
                data = json.loads(post.string)
                target_url = data["mainEntityOfPage"]["@id"]
                url_collection.append(target_url)
        # logic of month and year calculation
        if current_month < 12:
            current_month += 1
        else:
            current_month = 1
            current_year += 1
    # save gathered urls
    with open("data/url_list.txt", "w") as f:
        for url in url_collection:
            f.write(f"{url}\n")


def get_youtube_urls(channels: list, verbose=False):
    """
    this functions saves all video urls from the input channel list to a file
    :param channels: a list of youtube channels
    :return: None
    """
    urls = []
    for chan in channels:
        c = Channel(chan)
        name = chan.split("/")[-1]
        num_videos = len(c.video_urls)
        for vid in tqdm(c.videos, total=num_videos, desc=name):
            if all(keyword in vid.title.lower() for keyword in ["no commentary", "full game", "gameplay"]):
                urls.append(vid.watch_url)

    with open("temp/urls.txt", "w") as f:
        for url in urls:
            f.write(f"{url}\n")


channel_list = [
    "https://www.youtube.com/@glp",
    "https://www.youtube.com/@MKIceAndFire",
    "https://www.youtube.com/@FullPlaythroughs",
    "https://www.youtube.com/@Shirrako"
]

get_wiki_urls()
get_youtube_urls(channel_list)
