import os
import re
import sys
from datetime import datetime
from typing import List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag

from royalroad import FictionSnapshot

def parseSpanToInt(title, html) -> int:
    return int(html.find('span', string=re.compile(f'[0-9]+ {title}')).string.split(' ')[0].replace(',', ''))

def extract_description(div) -> str:
    for br in div.find_all('br'):
        br.replace_with('\n')
    for hr in div.find_all('hr'):
        hr.replace_with('\n\n')
    text = div.get_text()
    return text

# snapshot_time, url, cover_url, title, description, tags, pages, chapters, rating, from_url, from_ranking
def snapshot_fiction(fiction : Tag, snapshot_time : datetime, from_url : str, rank : int) -> FictionSnapshot:
    try:
        stats = fiction.find('div', class_="stats")
        followers = parseSpanToInt('Followers', stats)
        views = parseSpanToInt('Views', stats)
        parsed = urlparse(from_url)
        baseurl = f"{parsed.scheme}://{parsed.netloc}"
        return FictionSnapshot(
            snapshot_time = snapshot_time,
            url = baseurl + fiction.find('h2', class_='fiction-title').find('a')['href'],
            cover_url = fiction.find('img')['src'],
            title = fiction.find('h2', class_='fiction-title').text.strip(),
            description = extract_description(fiction.find('div', id=re.compile('^description-'))),
            tags = ','.join([x.text for x in fiction.find_all('a', class_="fiction-tag")]),
            pages = parseSpanToInt('Pages', stats),
            chapters = parseSpanToInt('Chapters', stats),
            rating = float(stats.find('span', class_="star")['title']),
            from_url = from_url,
            from_ranking = rank
        )
    except Exception as e:
        print(f"Error in snapshot_fiction: {e}")
        raise e

def snapshot_page(html_text, from_url) -> List[FictionSnapshot]:
    try:
        snapshot_time = datetime.now()

        soup = BeautifulSoup(html_text, 'html.parser')
        html_soups = soup.find_all(class_='fiction-list-item')

        fictions = []
        for (rank, html_soup) in enumerate(html_soups, start=1):
            fictions.append(snapshot_fiction(
                html_soup,
                snapshot_time = snapshot_time,
                from_url = from_url,
                rank = rank
            ))
        return fictions
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        filename = exc_tb.tb_frame.f_code.co_filename
        print(f"Exception '{e}' occurred at line {line_number} in {filename}")
        return []

def snapshot_url(url) -> List[FictionSnapshot]:
    try:
        page = requests.get(url)
        return snapshot_page(page.text, url)
    except Exception as e:
        print(f"Error in snapshot_url: {e}")
        return []

def download_rising_stars(path):
    req = requests.get('https://www.royalroad.com/fictions/rising-stars')
    with open(path, 'x') as f:
        f.write(req.text)

def check_on_download():
    test_file = '../test/rising-stars.html'
    if not os.path.exists(test_file):
        print("Downloading rising stars...")
        download_rising_stars(test_file)
    with open(test_file, 'r') as file:
        text = file.read()
    snapshots = snapshot_page(text, 'file:///./rising-stars.html')
    print(snapshots)

def check_on_url():
    snapshots = snapshot_url('https://www.royalroad.com/fictions/rising-stars')
    print(snapshots)

if __name__ == "__main__":
    check_on_download()
    # check_on_url()
