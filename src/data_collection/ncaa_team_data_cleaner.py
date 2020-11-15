"""
Script to clean, sort and preprocess NCAA team data
Author: Atharv Sonwane
"""

import pandas as pd
import os
from pathlib import Path
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-y", "--year", type=int, required=True)
parser.add_argument("--all", action="store_true")
parser.add_argument("--alpha", type=float, default=None)
parser.add_argument("--window", type=int, default=None)
parser.add_argument("--clean", action="store_true")
parser.add_argument("--tf_sme", action="store_true")
parser.add_argument("--tf_cme", action="store_true")
parser.add_argument("--tf_ewm", action="store_true")
parser.add_argument("--combine_vanilla", action="store_true")
parser.add_argument("--combine_sme", action="store_true")
parser.add_argument("--combine_cme", action="store_true")
parser.add_argument("--combine_ewm", action="store_true")
args = parser.parse_args()

year = args.year
alpha = 0.2 if args.all and args.alpha is None else args.alpha
window = 10 if args.all and args.window is None else args.window

user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"
features = ["Kills", "Errors", "Total Attacks", "Hit Pct", "Assists", "Aces", "SErr", "Digs", "RErr", "Block Solos", "Block Assists", "BErr", "PTS"]
combined_features = ["Date", "TeamA", "TeamB", "Result", "S", "Team A Kills", "Team A Errors", "Team A Total Attacks", "Team A Hit Pct", "Team A Assists", "Team A Aces", "Team A SErr", "Team A Digs", "Team A RErr", "Team A Block Solos", "Team A Block Assists", "Team A BErr", "Team A PTS", "Team B Kills", "Team B Errors", "Team B Total Attacks", "Team B Hit Pct", "Team B Assists", "Team B Aces", "Team B SErr", "Team B Digs", "Team B RErr", "Team B Block Solos", "Team B Block Assists", "Team B BErr", "Team B PTS"]

data_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.joinpath(f"data/ncaa/")


def clean_data():
    print(f"Cleaning team data for {year} ...", end=' ')
    for root, _, files in os.walk(data_path.joinpath(f'/raw/{year}/team_game_by_game/')):
        for i in range(len(files), desc='Cleaning data'):
            f = files[i]
            df = pd.read_csv(Path(root).joinpath(f), header=1)
            if year >= 2018:
                df.drop(columns=["MP", "Attend", "BHE", "Unnamed: 20"], inplace=True)
            else:
                df.drop(labels=["MP", "BHE", "Unnamed: 19"], axis=1, inplace=True)
            df.replace({'/':''}, regex=True, inplace=True)
            df.fillna(0, inplace=True)
            df[["Kills", "Errors", "Total Attacks", "Assists", "Aces", "SErr", "Digs", "RErr", "Block Solos", "Block Assists", "BErr"]] = df[["Kills", "Errors", "Total Attacks", "Assists", "Aces", "SErr", "Digs", "RErr", "Block Solos", "Block Assists", "BErr"]].astype(int)
            outpath = Path(root).parent.parent.parent.joinpath(f"processed/{year}/game_by_game_cleaned/")
            outpath.mkdir(parents=True, exist_ok=True)
            f = f[:f.find('(') - 1] + ".csv"
            df.to_csv(outpath.joinpath(f), index=False)
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


def transform_team_data(input_dir, output_dir, tf):
    print(f"Transforming data from {input_dir} to {output_dir} using {tf.__name__} ...", end=' ')
    for root, _, files in os.walk(input_dir):
        new_root = Path(output_dir)
        new_root.mkdir(parents=True, exist_ok=True)
        for f in files:
            df = pd.read_csv(Path(root).joinpath(f))
            tf(df)
            df.to_csv(new_root.joinpath(f), index=False)
    print("Done!")

def sma(df):
    df[features] = df[features].rolling(window, min_periods=1).mean()

def cma(df):
    df[features] = df[features].expanding().mean()

def ewm(df):
    df[features] = df[features].ewm(alpha=alpha).mean()


def combine(input_path, output_path):
    print("Combining data directly for team matches ...", end=' ')
    dfs = []
    team_names = []
    for root, dirs, files in os.walk(input_path):
        for f in files:
            team_names.append(f[:-4])
            dfs.append(pd.read_csv(Path(root).joinpath(f)))

    data = []

    err_a = 0
    err_b = 0

    for i, name in enumerate(team_names):
        df = dfs[i]
        for _, TeamA_row in df.iterrows(): 
            date = TeamA_row["Date"]
            TeamA = name
            TeamB = clean_name(TeamA_row["Opponent"])
            Result = 1 if TeamA_row["Result"][0] == 'W' else 0
            S = TeamA_row["S"]
            TeamA_stats = TeamA_row[features]
            try:
                TeamB_df = dfs[team_names.index(TeamB)]
            except:
                err_a += 1
                continue
            try:
                TeamB_row = TeamB_df[(TeamB_df["Date"] == date) & TeamB_df["Opponent"].str.contains(TeamA)].reset_index().loc[0]
            except:
                err_b += 1
                continue

            TeamB_stats = TeamB_row[features]
            data.append([date, TeamA, TeamB, Result, S, *TeamA_stats, *TeamB_stats])
        
    combined_df = pd.DataFrame(data, columns=combined_features)
    combined_df.to_csv(output_path, index=False)
    results = dict(df_length=len(combined_df), err_a=err_a, err_b=err_b)
    print(f"Done! Results: {results}")
    return results


def prev_combine(input_path, output_path):
    print("Combing data using cumulatives for team matches ...", end=' ')
    dfs = []
    team_names = []
    for root, _, files in os.walk(input_path):
        for f in files:
            team_names.append(f[:-4])
            dfs.append(pd.read_csv(Path(root).joinpath(f)))

    data = []

    err_a = 0
    err_b = 0

    for i, name in enumerate(team_names):
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
            TeamA_stats = TeamA_row[features]
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

            TeamB_stats = TeamB_row[features]
            data.append([date, TeamA, TeamB, Result, S, *TeamA_stats, *TeamB_stats])
        
    combined_df = pd.DataFrame(data, columns=combined_features)
    combined_df.to_csv(output_path, index=False)
    results = dict(df_length=len(combined_df), err_a=err_a, err_b=err_b)
    print(f"Done! Results: {results}. Data stored at {output_path}")
    return results


if __name__=='__main__':
    if args.all or args.clean:
        clean_data()

    if args.all or args.tf_sme:
        transform_team_data(
            input_dir=data_path.joinpath(f"processed/{year}/game_by_game_cleaned"),
            output_dir=data_path.joinpath(f"processed/{year}/game_by_game_{window}_sma"),
            tf=sma,
        )
    
    if args.all or args.tf_cme:
        transform_team_data(
            input_dir=data_path.joinpath(f"processed/{year}/game_by_game_cleaned"),
            output_dir=data_path.joinpath(f"processed/{year}/game_by_game_cma"),
            tf=cma,
        )
    
    if args.all or args.tf_ewm:
        transform_team_data(
            input_dir=data_path.joinpath(f"processed/{year}/game_by_game_cleaned"),
            output_dir=data_path.joinpath(f"processed/{year}/game_by_game_{alpha}_ewm"),
            tf=ewm,
        )
    
    if args.all or args.combine_vanilla:
        combine(
            input_path=data_path.joinpath(f"processed/{year}/game_by_game_cleaned"),
            output_path=data_path.joinpath(f"processed/{year}/accumulated/matches_gathered.csv"),
        )
    
    if args.all or args.combine_sme:
        prev_combine(
            input_path=data_path.joinpath(f"processed/{year}/game_by_game_{window}_sma"),
            output_path=data_path.joinpath(f"processed/{year}/accumulated/{window}_sma.csv"),
        )

    if args.all or args.combine_cme:
        prev_combine(
            input_path=data_path.joinpath(f"processed/{year}/game_by_game_{window}_sma"),
            output_path=data_path.joinpath(f"processed/{year}/accumulated/{window}_sma.csv"),
        )
    
    if args.all or args.combine_ewm:
        prev_combine(
            input_path=data_path.joinpath(f"processed/{year}/game_by_game_{window}_sma"),
            output_path=data_path.joinpath(f"processed/{year}/accumulated/{window}_sma.csv"),
        )
