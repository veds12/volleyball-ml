"Author : Vedant Shah"
"Data to scrape NCAA Women's Volleyball stats"


import re
from urllib.request import Request, urlopen

import pandas as pd
import requests
from bs4 import BeautifulSoup

user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"

url_team_map = {
    "Baylor": "https://stats.ncaa.org/teams/481920",  # Use links according to the year
    "Stanford": "https://stats.ncaa.org/teams/481752",
    "Wisconsin": "https://stats.ncaa.org/teams/481833",
    "Texas_A&M": "https://stats.ncaa.org/teams/481771",
    "Pittsburgh": "https://stats.ncaa.org/team/545.0/14942",
    "Minnesota": "https://stats.ncaa.org/team/428.0/14942",
    "Nebraska": "https://stats.ncaa.org/teams/482137",
    "Washington": "https://stats.ncaa.org/teams/481815",
    "Kentucky": "https://stats.ncaa.org/team/334.0/14942",
    "Florida": "https://stats.ncaa.org/team/235.0/14942",
}

print("<-------Starting Data Scraping------->")
for team_name, root_url in url_team_map.items():
    req = Request(root_url, headers={"User-Agent": user_agent})
    root_page = urlopen(req)
    root_html = root_page.read().decode("utf-8")
    soup = BeautifulSoup(root_html, "lxml")
    game_by_game_url = "https://stats.ncaa.org" + str(
        soup.find("body").find("div", id="contentarea").contents[17]["href"]
    )
    r = requests.get(game_by_game_url, headers={"User-Agent": user_agent})
    tables = pd.read_html(r.text)
    df = tables[-1].drop(labels=[0], axis=0)
    path = "./../data/ncaa/game_by_game_" + team_name + ".csv"
    df.to_csv(path, index=False)
    print(f"{team_name} - Scraped!")
print("<-------Data Scraped!------->")
