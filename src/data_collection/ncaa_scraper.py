"""
Author : Vedant Shah
Script to scrape NCAA Women's Volleyball stats
"""

import re
from urllib.request import Request, urlopen
import argparse
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import os

parser = argparse.ArgumentParser()
parser.add_argument("-y", "--year", type=int, required=True)
args = parser.parse_args()

year = args.year

user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"

data_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.joinpath(f"data/ncaa")
index_path = data_path.joinpath(f"index_files/ncaa_{year}_teams_index.html")
soup = BeautifulSoup(open(index_path, "r"), "lxml")
a_list = soup.body.find('div', id='contentarea').find('div', id='national_ranking_div').find_all('a', href=True)
a_list = a_list[3:]

root_path = data_path.joinpath(f"{year}")
root_path.mkdir(parents=True, exist_ok=True)
root_path.joinpath("team_game_by_game").mkdir(exist_ok=True, parents=True)
root_path.joinpath("team_stats").mkdir(exist_ok=True, parents=True)

root_url_main = "https://stats.ncaa.org"
url_teams_map = {tag.string : root_url_main + tag['href'] for tag in a_list}

print("<-------Starting Team Data Scraping------->\n")

for team_name, root_url in url_teams_map.items():
    req = Request(root_url, headers={"User-Agent": user_agent})
    root_page = urlopen(req)
    root_html = root_page.read().decode("utf-8")
    soup = BeautifulSoup(root_html, "lxml")
    team_stats_idx = 15 if year >= 2018 else 13
    team_stats_url = "https://stats.ncaa.org" + str(
        soup.find("body").find("div", id="contentarea").contents[team_stats_idx]["href"]
    )
    game_by_game_idx = 17 if year >= 2018 else 15
    game_by_game_url = "https://stats.ncaa.org" + str(
        soup.find("body").find("div", id="contentarea").contents[game_by_game_idx]["href"]
    )
    r = requests.get(game_by_game_url, headers={"User-Agent": user_agent})
    tables = pd.read_html(r.text)
    df = tables[-1].drop(labels=[0], axis=0)
    df.to_csv(root_path.joinpath(f"team_game_by_game/{team_name}.csv"), index=False)

    r = requests.get(team_stats_url, headers={"User-Agent": user_agent})
    tables = pd.read_html(r.text)
    df = tables[1]
    df.to_csv(root_path.joinpath(f"team_stats/{team_name}.csv"), index=False)
    print(f"{team_name} - Scraped!")

print("\n<-------Data Scraped!------->")
