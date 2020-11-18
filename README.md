# volleyball-ml

## Usage 

Example to generate the data and train the model for the year 2019. Run the code in the root of the project folder :

```python
python src/data_collection/ncaa_team_scraper.py -y 2019
python src/data_collection/ncaa_player_scraper.py -y 2019
python src/data_collection/ncaa_team_data_cleaner.py -y 2019 --all
python src/data_collection/ncaa_player_data_cleaner.py -y 2019 --all
python src/models/ncaa_model_evaluator.py -d "../../data/ncaa/processed/2019/accumulated/0.2_ewm_with_players.csv"
python src/models/ncaa_model_tuner.py -d "../../data/ncaa/processed/2019/accumulated/0.2_ewm_with_players.csv"
```

## Description of relevant scripts

#### Final Scripts

##### ncaa_team_scraper.py : 
* Scrapes game by game data and team statistics for all the teams
* Data location : data/ncaa/raw/
  
##### ncaa_player_scraper.py : 
* Scrapes individual player performance data 
* Data location : data/ncaa/raw

##### ncaa_team_data_cleaner.py :
* Cleans and preprocesses team data and creates team_vs_team (without players stats) dataset s
* Data location : data/ncaa/processed/{year}, data/ncaa/processed/{year}/accumulated

##### ncaa_team_player_cleaner.py :
* Cleans and preprocesses team data and creates team_vs_team (with player stats) dataset 
* Data location : data/ncaa/processed/{year}, data/ncaa/processed/{year}/accumulated

##### ncaa_model_evaluator.py :
* Evaluates five different machine learning models on the dataset present at the entered path

##### ncaa_model_tuner.py :
* Experiments with tuning and feature selection on the dataset and different models

#### Other scripts

##### ncaa_combine_data(deprecated).py
* Generates a dataset with data compiled over all the years

##### clean_team_stats_filenames.py
* Cleans the filenames in the data/ncaa/raw/{year}/team_stats directory 
* Needed before using ncaa_combine_data(deprecated).py

##### src/models/experiments
* Random experiments with different data, models and techniques

## Contributors 

* [Atharv Sonwane](https://github.com/threewisemonkeys-as)
* [Atharv Kirtikar](https://github.com/Meloninga54)
* [Himay Patel](https://github.com/Meloninga54)
* [Vedant Shah](https://github.com/veds12)

