import requests
import pandas as pd

user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"

r = requests.get("https://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=14242&org_id=77&stats_player_seq=-100", headers={"User-Agent": user_agent})
df = pd.read_html(r.text)[-1].drop(labels=[0], axis=0)
df.to_csv("data/ncaa/raw/2018/team_game_by_game/BYU (WCC).csv", index=False)
