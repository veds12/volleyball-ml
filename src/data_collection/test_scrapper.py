import requests
import pandas as pd

user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"

r = requests.get("https://stats.ncaa.org/team/655/stats/12426", headers={"User-Agent": user_agent})
df = pd.read_html(r.text)[-1].drop(labels=[0], axis=0)
df.to_csv("data/ncaa/raw/2016/team_stats/Southeastern La..csv", index=False)

