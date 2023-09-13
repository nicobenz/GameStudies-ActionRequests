from bs4 import BeautifulSoup
import requests
import re

save_path = "data/transcripts/raw"

# import and prepare urls
with open("data/url_list.text", "r") as f:
    urls = f.readlines()
transcript_urls = [url.strip() for url in urls]
transcript_urls.sort()

for transcript_num, url in enumerate(transcript_urls, start=1):
    # get content of url
    content = requests.get(url)
    soup = BeautifulSoup(content.text, "html.parser")

    # get title for filename
    title = soup.head.title.text.split(" ")
    title = '_'.join(title)
    title = title.replace("&", "and")
    title = re.sub(r'[^a-zA-Z0-9_]', '', title)
    save_name = f"{transcript_num:03d}_{title}.txt"
    # extract and save relevant text
    roi = soup.find_all("div", class_="post-body entry-content float-container")
    text = [element.get_text() for element in roi]
    if len(text) > 1:
        text = "\n\n\n".join(text)
    else:
        text = text[0]

    with open(f"{save_path}/{save_name}", "w") as f:
        f.write(text)
