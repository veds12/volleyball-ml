"""
Script to collect data from the 2019 Women's Volleyball World Cup
Author: Atharv Sonwane
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import os

index_url = "https://www.volleyball.world/en/volleyball/worldcup/2019/women/schedule"

match_stats_header = [
    "Match Num",
    "Team",
    "Opponent",
    "Set 1 Duration",
    "Set 1 Scored",
    "Set 1 Against",
    "Set 2 Duration",
    "Set 2 Scored",
    "Set 1 Against",
    "Set 3 Duration",
    "Set 3 Scored",
    "Set 3 Against",
    "Attack",
    "Block",
    "Serve",
    "Opp. Errors",
    "Total",
    "Dig",
    "Reception",
    "Set",
]
match_stats = pd.DataFrame(columns=match_stats_header)
players_stats_by_match = {}

user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"
headers = {"User-Agent": user_agent}

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
data_path = current_path.parent.parent.joinpath(f"data/fivb")
match_stats_fname = "2019_women_world_cup_match-wise.csv"
player_stats_fname = "2019_women_world_cup_player-wise.csv"
matches_data_fname = "2019_women_world_cup_matches.csv"

start_time = datetime.now()
print(f"Starting scraping process at {start_time:%d/%m/%y %H:%M:%S}.")


print(f"\nFetching match list and urls from {index_url} ...", end=" ")
r = requests.get((index_url), headers=headers)
html = r.text
soup = BeautifulSoup(html, "lxml")
data = json.loads(
    '{"raw": ['
    + soup.find("div", class_="col-1-1 schedulepage").find("script").string[75:-1753]
    + "]}"
)["raw"]
match_urls = ["https://www.volleyball.world/" + match["Url"] for match in data]

matches_dict = {
    "Match Num": [match["MatchNumber"] for match in data],
    "TeamA": [match["TeamA"]["Code"] for match in data],
    "TeamB": [match["TeamB"]["Code"] for match in data],
    "TeamA Score": [match["MatchPointsA"] for match in data],
    "TeamB Score": [match["MatchPointsB"] for match in data],
    "Winner": [0 if match["MatchPointsA"] > match["MatchPointsB"] else 1 for match in data]
}
matches_df = pd.DataFrame(matches_dict)
matches_df.to_csv(data_path.joinpath(matches_data_fname), index=False)
print("Complete!")

for url in match_urls:
    print(f"\nFetching from {url} ...", end=" ")
    r = requests.get((url), headers=headers)
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    print("Complete!")

    print("\tProcessing header ...", end=" ")
    match_info = json.loads(
        soup.find("div", class_="fivb-single-match").find("script").string[49:-23]
    )["raw"]
    match_num = int(match_info["MatchNumber"])
    teamA = match_info["TeamA"]["Code"]
    teamB = match_info["TeamB"]["Code"]
    sets_info = match_info["Sets"]
    teamA_stats = {
        "Match Num": match_num,
        "Team": teamA,
        "Set 1 Duration": int(sets_info[0]["Minutes"]),
        "Opponent": teamB,
        "Set 1 Scored": sets_info[0]["PointsA"],
        "Set 1 Against": sets_info[0]["PointsB"],
        "Set 2 Duration": int(sets_info[1]["Minutes"]),
        "Set 2 Scored": sets_info[1]["PointsA"],
        "Set 1 Against": sets_info[1]["PointsB"],
        "Set 3 Duration": int(sets_info[2]["Minutes"]),
        "Set 3 Scored": sets_info[2]["PointsA"],
        "Set 3 Against": sets_info[2]["PointsB"],
    }
    teamB_stats = {
        "Match Num": match_num,
        "Team": teamB,
        "Set 1 Duration": int(sets_info[0]["Minutes"]),
        "Opponent": teamA,
        "Set 1 Scored": sets_info[0]["PointsB"],
        "Set 1 Against": sets_info[0]["PointsA"],
        "Set 2 Duration": int(sets_info[1]["Minutes"]),
        "Set 2 Scored": sets_info[1]["PointsB"],
        "Set 1 Against": sets_info[1]["PointsA"],
        "Set 3 Duration": int(sets_info[2]["Minutes"]),
        "Set 3 Scored": sets_info[2]["PointsB"],
        "Set 3 Against": sets_info[2]["PointsA"],
    }
    print(
        f"Match Number: {match_num} | TeamA: {teamA} | TeamB: {teamB} | Score: {match_info['MatchPointsA']}-{match_info['MatchPointsB']}"
    )

    print("\tProcessing teamwise data ...", end=" ")
    game_stats_labels = [
        i.text for i in soup.find_all("div", class_="fivb-stats__label")
    ][:-2]
    game_stats = [
        int(i.find("span").text)
        for i in soup.find_all("span", class_="fivb-stats__progress")
    ]
    for j, label in enumerate(game_stats_labels):
        teamA_stats[label] = game_stats[2 * j]
        teamB_stats[label] = game_stats[2 * j + 1]
    match_stats.loc[2 * match_num] = teamA_stats
    match_stats.loc[2 * match_num + 1] = teamB_stats
    print("Complete!")

    print("\tProcessing playerwise data ...", end=" ")
    players_df, players_df_raw = {}, {}
    players_df_raw[teamA], players_df_raw[teamB], _ = pd.read_html(html)
    players_df[teamA], players_df[teamB] = pd.DataFrame(), pd.DataFrame()
    final_col_names = [
        "Number",
        "Name",
        "Points Scored",
        "Attacks Won",
        "Attacks Attempted",
        "Blocks Won",
        "Blocks Attempted",
        "Serves Won",
        "Serves Attempted",
    ]
    raw_col_names = [
        ("N°", "Unnamed: 0_level_1"),
        ("Name", "Unnamed: 1_level_1"),
        ("Points", "Unnamed: 7_level_1"),
        ("Attack", "1"),
        ("Attack", "2"),
        ("Block", "3"),
        ("Block", "4"),
        ("Serve", "5"),
        ("Serve", "Won"),
    ]
    for team in (teamA, teamB):
        players_df[team]["Match Num"] = [match_num] * len(players_df_raw[team])
        players_df[team]["Team"] = [team] * len(players_df_raw[team])
        for source, dest in zip(raw_col_names, final_col_names):
            players_df[team][dest] = players_df_raw[team][source]
        if team not in players_stats_by_match.keys():
            players_stats_by_match[team] = []
        players_stats_by_match[team].append(players_df[team])
    print("Complete!")


print("\nStoring collected data")

print(f"Creating {data_path.absolute()} to store data in ...", end=" ")
Path(data_path).mkdir(exist_ok=True, parents=True)
print("Complete!")

print(
    f"\tStoring matchwise stats at {data_path.joinpath(match_stats_fname).absolute()} ...",
    end=" ",
)
match_stats.to_csv(data_path.joinpath(match_stats_fname), index=False)
print("Complete!")

print(
    f"\tStoring playerwise stats in {data_path.joinpath(player_stats_fname).absolute()} ...",
    end=" ",
)
players_df_list = []
for i in players_stats_by_match.values():
    for j in i:
        players_df_list.append(j)
player_stats = pd.concat(players_df_list).to_csv(data_path.joinpath(player_stats_fname), index=False)
print("Complete!")

print(
    f"\nScraping Complete for {len(match_urls)} url(s). Took {(datetime.now()-start_time).seconds}"
)
