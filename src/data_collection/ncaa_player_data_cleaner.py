"""
Script to clean, sort and preprocess NCAA player data
Author: Atharv Sonwane
"""

import pandas as pd
import os
from pathlib import Path
import argparse
import requests


parser = argparse.ArgumentParser()
parser.add_argument("-y", "--year", type=int, required=True)
parser.add_argument("--all", action="store_true")
parser.add_argument("--alpha", type=float, default=0.2)
parser.add_argument("--window", type=int, default=10)
parser.add_argument("--clean", action="store_true")
parser.add_argument("--tf_sma", action="store_true")
parser.add_argument("--tf_cma", action="store_true")
parser.add_argument("--tf_ewm", action="store_true")
parser.add_argument("--combine_vanilla", action="store_true")
parser.add_argument("--combine_sma", action="store_true")
parser.add_argument("--combine_cma", action="store_true")
parser.add_argument("--combine_ewm", action="store_true")
args = parser.parse_args()

year = args.year
alpha = 0.2 if args.all and args.alpha is None else args.alpha
window = 10 if args.all and args.window is None else args.window

user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"
features = ["Kills", "Errors", "Total Attacks", "Hit Pct", "Assists", "Aces", "SErr", "Digs", "RErr", "Block Solos", "Block Assists", "BErr", "PTS"]
player_features = [f"Player {j} {f}" for f in features for j in range(12)]
combined_features = [
"Date", "TeamA", "TeamB", "Result", "S", "Team A Kills", "Team A Errors", "Team A Total Attacks", "Team A Hit Pct", "Team A Assists", "Team A Aces", "Team A SErr", "Team A Digs",  "Team A RErr", "Team A Block Solos", "Team A Block Assists", "Team A BErr", "Team A PTS", "Team B Kills", "Team B Errors", "Team B Total Attacks", "Team B Hit Pct", "Team B Assists", "Team B Aces", "Team B SErr", "Team B Digs", "Team B RErr", "Team B Block Solos", "Team B Block Assists", "Team B BErr", "Team B PTS",
*[f"Team A {s}" for s in player_features],
*[f"Team B {s}" for s in player_features]
]

data_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.joinpath(f"data/ncaa/")


def clean_data():
    print("Cleaning player data ...", end=' ')
    for root, dirs, _ in os.walk(data_path.joinpath(f"raw/{year}/player_game_wise/")):
        for team_dir in dirs:
            team_root, _, player_files = list(os.walk(Path(root).joinpath(team_dir)))[0]
            team_name = Path(team_root).name
            team_name = team_name[:team_name.find('(') - 1]
            for player_file in player_files:
                outpath = Path(root).parent.parent.parent.joinpath(f"processed/{year}/player_game_wise_cleaned/{team_name}")
                if outpath.joinpath(player_file).is_file():
                    continue
                try:
                    df = pd.read_csv(Path(team_root).joinpath(player_file), header=1)
                except:
                    print(f"{Path(team_root).joinpath(player_file)} Failed!")
                    continue
                
                if year > 2017:
                    df.drop(columns=["MP", "Attend", "BHE", "Unnamed: 20"], inplace=True)
                else:
                    df.drop(columns=["MP", "BHE", "Unnamed: 19"], inplace=True)

                df.replace({'/':''}, regex=True, inplace=True)
                df.fillna(0, inplace=True)
                df[["Kills", "Errors", "Total Attacks", "Assists", "Aces", "SErr", "Digs", "RErr", "Block Solos", "Block Assists", "BErr"]] = df[["Kills", "Errors", "Total Attacks", "Assists", "Aces", "SErr", "Digs", "RErr", "Block Solos", "Block Assists", "BErr"]].astype(int)
                outpath.mkdir(parents=True, exist_ok=True)
                df.to_csv(outpath.joinpath(player_file), index=False)

    for root, dirs, _ in os.walk(data_path.joinpath(f"processed/{year}/player_game_wise_cleaned")):
        for team_dir in dirs:
            for team_root, _, player_files in os.walk(Path(root).joinpath(team_dir)):
                for player_file in player_files:
                    if player_file[player_file.find(".csv") - 1] == ' ':
                        cp = Path(team_root).joinpath(player_file)
                        n = player_file[:player_file.find(".csv") - 1] + ".csv"
                        cp.rename(cp.parent.joinpath(n))
    print("Done!")


def store_player(url, path):
    print(f"Fetching for {Path(path).name[:-4]} ...", end=' ')
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"})
    pd.read_html(r.text)[-1].drop(labels=[0], axis=0).to_csv(path, index=False)
    print("Done!")


def clean_name(name):
    name = name.replace('\"', '')
    if '@' in name:
        if name.index('@') == 0:
            return name[2:]
        else:
            return name[:name.index('@')-1]
    else:
        return name


def transform_player_data(input_dir, output_dir, tf):
    print(f"Transforming data from {input_dir} to {output_dir} using {tf.__name__} ...", end=' ')
    for root, dirs, _ in os.walk(input_dir):
        for team_dir in dirs:
            for team_root, _, player_files in os.walk(Path(root).joinpath(team_dir)):
                for player_file in player_files:
                    df = pd.read_csv(Path(team_root).joinpath(player_file))
                    outpath = Path(output_dir).joinpath(team_dir)
                    tf(df)
                    outpath.mkdir(parents=True, exist_ok=True)
                    df.to_csv(outpath.joinpath(player_file), index=False)
    print("Done!")

def sma(df):
    df[features] = df[features].rolling(window, min_periods=1).mean()

def cma(df):
    df[features] = df[features].expanding().mean()

def ewm(df):
    df[features] = df[features].ewm(alpha=alpha).mean()


def combine_with_player(player_input_path, team_stats_path, team_matches_path, macthes_with_player_info_path, combined_output_path):
    print(f"Combining player data for individual teams into {combined_output_path} -")

    print("\tBuilding team index ...", end=' ')
    team_names = []
    for root, _, files in os.walk(team_stats_path):
        for f in files:
            team_names.append(f[:-4])
    print("Done!")
    print(team_names)

    player_input_path = Path(player_input_path)
    team_stats_path = Path(team_stats_path)
    team_matches_path = Path(team_matches_path)
    macthes_with_player_info_path = Path(macthes_with_player_info_path)
    macthes_with_player_info_path.mkdir(exist_ok=True, parents=True)

    print("\tSorting team data ...", end=' ')
    for i, name in enumerate(team_names):
        team_matches_df = pd.read_csv(team_matches_path.joinpath(f"{name}.csv"))
        team_stats_df = pd.read_csv(team_stats_path.joinpath(f"{name}.csv"))
        top_player_names = [] 
        for j, (_, player_row) in enumerate(team_stats_df[(team_stats_df["Player"] != "TEAM") & (team_stats_df["Player"] != "Totals") & (team_stats_df.Player != "Opponent Totals")].sort_values(by=["GP"], ascending=False).iterrows()):
            top_player_names.append(player_row["Player"])
            if j == 11:
                break
        if len(top_player_names) < 12:
            print(f"Could not get enough players for {name}!")
            continue
        try:
            for j, player in enumerate(top_player_names):
                team_matches_df[[f"Player {j} {f}" for f in features]] = pd.read_csv(player_input_path.joinpath(f"{name}/{player}.csv"))[features]
            team_matches_df.to_csv(macthes_with_player_info_path.joinpath(f"{name}.csv"), index=False)        
        except:
            print(f"\nFailed to get player {player} for {name}!")
            continue
    print("Done!")

    print("\tGetting match wise dataframes ...", end=' ')
    dfs = []
    team_names = []
    for root, _, files in os.walk(macthes_with_player_info_path):
        for f in files:
            team_names.append(f[:-4])
            dfs.append(pd.read_csv(Path(root).joinpath(f)))
    print(f"Collected {len(dfs)} dataframes. Done!")

    err_a, err_b = 0, 0
    data = []
    print("\tCombining into a single df ...", end=' ')
    for i in range(len(dfs)):
        name = team_names[i]
        df = dfs[i]
        for j in range(len(df)):
            if j == 0:
                continue
            TeamA_row = df.loc[j-1]
            date = TeamA_row["Date"]
            TeamA = name
            TeamB = clean_name(TeamA_row["Opponent"])
            Result = 1 if TeamA_row["Result"][0] == 'W' else 0
            S = TeamA_row["S"]
            TeamA_stats = TeamA_row[features + player_features]
            try:
                TeamB_df = dfs[team_names.index(TeamB)]
            except:
                err_a += 1
                continue
            try:
                TeamB_row_index = TeamB_df[(TeamB_df["Date"] == date) & TeamB_df["Opponent"].str.contains(TeamA)].index[0]
                if TeamB_row_index == 0:
                    continue
                TeamB_row = TeamB_df.loc[TeamB_row_index-1]
            except:
                err_b += 1
                continue

            TeamB_stats = TeamB_row[features + player_features]
            data.append([date, TeamA, TeamB, Result, S, *TeamA_stats, *TeamB_stats])

    combined_df = pd.DataFrame(data, columns=combined_features)
    combined_df.to_csv(combined_output_path, index=False)
    results = dict(df_len=len(combined_df), err_a=err_a, err_b=err_b)
    print(f"Done! Results = {results}")
    return results

if __name__=='__main__':
    if args.all or args.clean:
        clean_data()

    if args.all or args.tf_sma:
        transform_player_data(
            input_dir=data_path.joinpath(f"processed/{year}/player_game_wise_cleaned"),
            output_dir=data_path.joinpath(f"processed/{year}/player_game_wise_{window}_sma"),
            tf=sma,
        )
    
    if args.all or args.tf_cma:
        transform_player_data(
            input_dir=data_path.joinpath(f"processed/{year}/player_game_wise_cleaned"),
            output_dir=data_path.joinpath(f"processed/{year}/player_game_wise_cma"),
            tf=cma,
        )
    
    if args.all or args.tf_ewm:
        transform_player_data(
            input_dir=data_path.joinpath(f"processed/{year}/player_game_wise_cleaned"),
            output_dir=data_path.joinpath(f"processed/{year}/player_game_wise_{alpha}_ewm"),
            tf=ewm,
        )
    
    if args.all or args.combine_sma:
        combine_with_player(
            player_input_path=data_path.joinpath(f"processed/{year}/player_game_wise_{window}_sma"),
            team_stats_path=data_path.joinpath(f"raw/{year}/team_stats"),
            team_matches_path=data_path.joinpath(f"processed/{year}/game_by_game_{window}_sma"),
            macthes_with_player_info_path=data_path.joinpath(f"processed/{year}/game_by_game_with_players_{window}_sma"),
            combined_output_path=data_path.joinpath(f"processed/{year}/accumulated/{window}_sme_with_players.csv"),
        )

    if args.all or args.combine_cma:
        combine_with_player(
            player_input_path=data_path.joinpath(f"processed/{year}/player_game_wise_cma"),
            team_stats_path=data_path.joinpath(f"raw/{year}/team_stats"),
            team_matches_path=data_path.joinpath(f"processed/{year}/game_by_game_cma"),
            macthes_with_player_info_path=data_path.joinpath(f"processed/{year}/game_by_game_with_players_cma"),
            combined_output_path=data_path.joinpath(f"processed/{year}/accumulated/cme_with_players.csv"),
        )
    
    if args.all or args.combine_ewm:
        combine_with_player(
            player_input_path=data_path.joinpath(f"processed/{year}/player_game_wise_{alpha}_ewm"),
            team_stats_path=data_path.joinpath(f"raw/{year}/team_stats"),
            team_matches_path=data_path.joinpath(f"processed/{year}/game_by_game_{alpha}_ewm"),
            macthes_with_player_info_path=data_path.joinpath(f"processed/{year}/game_by_game_with_players_{alpha}_ewm"),
            combined_output_path=data_path.joinpath(f"processed/{year}/accumulated/{alpha}_ewm_with_players.csv"),
        )

# #%%

# import os
# from pathlib import Path

# year = 2017
# for root, _, files in os.walk(f'../../data/ncaa/raw/{year}/team_stats/'):
#     for f in files:
#         f_new = f[:f.find('(') - 1] + ".csv"
#         os.rename(Path(root).joinpath(f), Path(root).joinpath(f_new))
#         print(f"{f} successfully renamed to {f_new}!")