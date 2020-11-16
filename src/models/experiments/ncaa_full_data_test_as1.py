"""
Experimentation with different models on combined player and match data
Author: Atharv Sonwane
"""

# %%
import os
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

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
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import RFECV
from sklearn.manifold import TSNE
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import fbeta_score
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import cross_validate
from sklearn.model_selection import cross_val_predict

data_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.parent.joinpath(f"data/ncaa/")

# %%

df = pd.read_csv(data_path.joinpath("processed/2019/accumulated/0.2_ewm_with_players.csv"))
features = []

# %%

X = df.drop(["Date", "TeamA", "TeamB", "S", "Result"], axis=1)
y = df["Result"]

X_scaled = StandardScaler().fit_transform(X, y)

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
