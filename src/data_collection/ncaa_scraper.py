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

parser = argparse.parser()
paser.add_argument("-y", "--year", type=int)
args = parser.parse_args()

year = args.year

user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"

soup = BeautifulSoup(open(f"ncaa_{year}_team_index.html", "r"), "lxml")
a_list = soup.body.find('div', id='contentarea').find('div', id='national_ranking_div').find_all('a', href=True)
a_list = a_list[3:]

root_url = "https://stats.ncaa.org"

url_teams_map = {tag.string : root_url + tag['href'] for tag in a_list}

print("<-------Starting Team Data Scraping------->\n")

for team_name, root_url in url_teams_map.items():
    req = Request(root_url, headers={"User-Agent": user_agent})
    root_page = urlopen(req)
    root_html = root_page.read().decode("utf-8")
    soup = BeautifulSoup(root_html, "lxml")
    team_stats_url = "https://stats.ncaa.org" + str(
        soup.find("body").find("div", id="contentarea").contents[15]["href"]
    )
    game_by_game_url = "https://stats.ncaa.org" + str(
        soup.find("body").find("div", id="contentarea").contents[17]["href"]
    )
    r = requests.get(game_by_game_url, headers={"User-Agent": user_agent})
    tables = pd.read_html(r.text)
    df = tables[-1].drop(labels=[0], axis=0)
    path = f"./../../data/ncaa/{year}/team_game_by_game/{team_name}.csv"
    df.to_csv(path, index=False)

    r = requests.get(team_stats_url, headers={"User-Agent": user_agent})
    tables = pd.read_html(r.text)
    df = tables[1]
    path = f"./../../data/ncaa/{year}/team_stats/{team_name}.csv"
    df.to_csv(path, index=False)
    print(f"{team_name} - Scraped!")

print("\n<-------Data Scraped!------->")
