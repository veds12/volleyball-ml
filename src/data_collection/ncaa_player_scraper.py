""" 
Author : Vedant Shah
Scipt to scrape individual game-wise performance data for each player
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

data_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.joinpath(f"data/ncaa/raw")
index_path = data_path.joinpath(f"index_files/ncaa_{year}_teams_index.html")
soup = BeautifulSoup(open(index_path, "r"), "lxml")
a_list = soup.body.find('div', id='contentarea').find('div', id='national_ranking_div').find_all('a', href=True)
a_list = a_list[3:]

root_path = data_path.joinpath(f"{year}")
root_path.mkdir(parents=True, exist_ok=True)
root_path = root_path.joinpath("player_game_wise")
root_path.mkdir(exist_ok=True, parents=True)

root_url_main = "https://stats.ncaa.org"
url_teams_map = {tag.string : root_url_main + tag['href'] for tag in a_list}

failed_list = []

print(f"Scraping NCAA Women's Player Volleyball Data for {year}\n")

i = 0
n = len(url_teams_map.values())
failed_players_list = []
failed_teams_list = []
for team_name, root_url in url_teams_map.items():
    i += 1
    print(f"[{i} / {n}] Scraping  {team_name} ...\n", end=' ')
    root_path.joinpath(f"{team_name}").mkdir(exist_ok=True, parents=True)

    try:
        req = Request(root_url, headers={"User-Agent": user_agent})
        root_page = urlopen(req)
        root_html = root_page.read().decode("utf-8")
        soup = BeautifulSoup(root_html, "lxml")
        team_stats_idx = 13 if year >= 2018 else 11
        team_roster_url = "https://stats.ncaa.org" + str(
            soup.find("body").find("div", id="contentarea").contents[team_stats_idx]["href"]
        )

        req_1 = Request(team_roster_url, headers={"User-Agent": user_agent})
        roster_page = urlopen(req_1)
        roster_html = roster_page.read().decode("utf-8")
        soup_roster = BeautifulSoup(roster_html, "lxml")

        a_list_players = soup_roster.body.find("div", id="contentarea").find("table").find_all("a", href=True)
        url_player_map = {tag.string : root_url_main + tag["href"] for tag in a_list_players}

        k = 0
        m = len(url_player_map)
        failed_list = []
        for player_name, player_url in url_player_map.items():
            k += 1
            print(f"\t[{k} / {m}] Scraping {player_name}...", end=' ')
            if root_path.joinpath(f"{team_name}/{player_name}.csv").exists():
                print("Exists!!")
                continue

            try:
                r = requests.get(player_url, headers={"User-Agent": user_agent})
                tables = pd.read_html(r.text)
                df = tables[-1].drop(labels=[0], axis=0)
                df.to_csv(root_path.joinpath(f"{team_name}/{player_name}.csv"), index=False)
                print("Scrapped!")
            except:
                print(f"Scraping for {player_name} failed!!")
                failed_list.append(player_name)
                print("\n")
        failed_players_list.append(failed_list)        
    except:
        print(f"Scraping failed for team {team_name}!!")
        failed_teams_list.append(team_name)

print(f"Scraping Completed! Data can be found at {root_path.resolve()}")

print(failed_players_list)
print(failed_teams_list)