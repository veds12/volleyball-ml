""" 
Script to clean file names
Author : Vedant Shah
"""

import pandas as pd
import os
from pathlib import Path
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-y", "--year", type=int, required=True)
args = parser.parse_args()
year = args.year

def clean_names():
    for root, _, files in os.walk(f'../../data/ncaa/raw/{year}/team_stats/'):
        for f in files:
            f_new = f[:f.find('(') - 1] + ".csv"
            os.rename(Path(root).joinpath(f), Path(root).joinpath(f_new))
            print(f"{f} successfully renamed to {f_new}!")

if __name__ == "__main__":
    clean_names()
