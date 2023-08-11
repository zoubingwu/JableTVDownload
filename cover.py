import requests
import os
import re
from bs4 import BeautifulSoup


def getCover(html_file, folder_path):
    # get cover
    soup = BeautifulSoup(html_file, "html.parser")
    cover_name = f"{os.path.basename(folder_path)}.jpg"
    cover_path = os.path.join(folder_path, cover_name)
    for meta in soup.find_all("meta"):
        meta_content = meta.get("content")
        if not meta_content:
            continue
        if "preview.jpg" not in meta_content:
            continue
        try:
            r = requests.get(meta_content)
            with open(cover_path, "wb") as cover_fh:
                r.raw.decode_content = True
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        cover_fh.write(chunk)
        except Exception as e:
            print(f"unable to download cover: {e}")

    print(f"cover downloaded as {cover_name}")


def make_legal_dir_name(name):
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = name.rstrip(". ")
    name = name.strip()
    if len(name) > 255:
       name = name[:255]
    return name


def getTitle(html_file):
    soup = BeautifulSoup(html_file, "html.parser")
    title = soup.select_one(".video-info .info-header .header-left h4")
    if title is not None:
        print("title: ", title)
        return make_legal_dir_name(title.text)
