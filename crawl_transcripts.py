from bs4 import BeautifulSoup
import requests

save_path = "data/transcripts"

# maybe find a way to automate getting the urls?
transcript_urls = [
    "https://game-scripts-wiki.blogspot.com/2022/01/medievil-1998-full-transcript.html"
]

for transcript_num, url in enumerate(transcript_urls, start=1):
    # get content of url
    content = requests.get(url)
    soup = BeautifulSoup(content.text, "html.parser")

    # get title for filename
    title = soup.head.title.text.split(" ")
    title = '_'.join(title)
    save_name = f"{transcript_num}_{title}.txt"

    # extract and save relevant text
    roi = soup.find_all("div", class_="post-body entry-content float-container")
    text = [element.get_text() for element in roi]
    if len(text) > 1:
        text = "\n\n\n".join(text)
    else:
        text = text[0]

    with open(f"{save_path}/{save_name}", "w") as f:
        f.write(text)
