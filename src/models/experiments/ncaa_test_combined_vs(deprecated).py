""" 
Training the models on the combined team data
Author : Vedant Shah
"""

# %%
import pandas as pd
import seaborn as sns
import sklearn
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import matplotlib.pyplot as plt
import torch
import pytorch_lightning as pl
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import RFECV
from sklearn.manifold import TSNE

# %%

features = ["Team A Kills", "Team A Errors", "Team A Total Attacks", "Team A Hit Pct", "Team A Assists", "Team A Aces", "Team A SErr", "Team A Digs", "Team A RErr", "Team A Block Solos", "Team A Block Assists", "Team A BErr", "Team A PTS", "Team B Kills", "Team B Errors", "Team B Total Attacks", "Team B Hit Pct", "Team B Assists", "Team B Aces", "Team B SErr", "Team B Digs", "Team B RErr", "Team B Block Solos", "Team B Block Assists", "Team B BErr", "Team B PTS"]

matches_gathered_df = pd.read_csv('../../../data/ncaa/combined/accumulated/matches_gathered.csv')
matches_gathered_X, matches_gathered_y = matches_gathered_df[features], matches_gathered_df["Result"]

sma_df = pd.read_csv('../../../data/ncaa/combined/accumulated/10_sma.csv')
sma_X, sma_y = sma_df[features], sma_df["Result"]

cma_df = pd.read_csv( '../../../data/ncaa/combined/accumulated/cma.csv')
cma_X, cma_y = cma_df[features], cma_df["Result"]

ewm_df = pd.read_csv('../../../data/ncaa/combined/accumulated/0.2_ewm.csv')
ewm_X, ewm_y = ewm_df[features], ewm_df["Result"]
# %%
data_dict = {
    "matches_gathered": (matches_gathered_X, matches_gathered_y),
    "sma": (sma_X, sma_y),
    "cma": (cma_X, cma_y),
    "ewm": (ewm_X, ewm_y),
}

# %%

def custom_eval(m, X, y, cv=StratifiedKFold(), metrics=("f1", "accuracy"), display_cm=True):
    print("\n--------------------------------------")
    print(f"Evaluating {m.__class__.__name__} -")
    scores = cross_validate(m, X, y, cv=cv, scoring=metrics)
    for metric in metrics:
        print(f"{metric} Mean: {scores[f'test_{metric}'].mean():.4f} Dev: {scores[f'test_{metric}'].std():.4f}")
    if display_cm:
        y_pred = cross_val_predict(m, X, y, cv=StratifiedKFold())
        cm = confusion_matrix(y, y_pred)
        plt.figure()
        plt.title(f"{m.__class__.__name__}")
        sns.heatmap(cm, annot=True)
        plt.show()
    print("--------------------------------------\n")

# %%
for name , (X, y) in data_dict.items():
    print(f"\n{name} -")
    custom_eval(LogisticRegression(), X, y)
    custom_eval(LogisticRegression(), X_scaled, y)

# %%

selector = SelectFromModel(estimator=LogisticRegression()).fit(X_scaled, y)
X_scaled_transformed = selector.fit_transform(X_scaled, y)

selected_features = [i for i in list(selector.get_support() * np.array(X.columns)) if i != '']
print(f"Selected {len(selected_features)} Features -\n{selected_features}")

custom_eval(LogisticRegression(), X_scaled_transformed, y)


# %%

models = [
    XGBClassifier(),
    RandomForestClassifier(),
    LogisticRegression(),
    LinearSVC(),
    DecisionTreeClassifier(),
]

for m in models:
    X_scaled_transformed = SelectFromModel(estimator=m).fit_transform(X_scaled, y)
    print(f"{m.__class__.__name__} selected {X_scaled_transformed.shape[-1]} features")
    custom_eval(m, X_scaled_transformed, y, display_cm=False)

# %%
