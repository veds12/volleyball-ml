"""
Experimentation with different models on combined player and match data
Author: Atharv Sonwane
"""

from inspect import Arguments
import os
from pathlib import Path
import argparse

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


def custom_eval(m, X, y, cv=StratifiedKFold(), metrics=("f1", "accuracy"), display_cm=True):
    print(f"\tEvaluating {m.__class__.__name__}", end=' ')
    scores = cross_validate(m, X, y, cv=cv, scoring=metrics)
    if display_cm:
        y_pred = cross_val_predict(m, X, y, cv=StratifiedKFold())
        cm = confusion_matrix(y, y_pred)
        plt.figure()
        plt.title(f"{m.__class__.__name__}")
        sns.heatmap(cm, annot=True)
        plt.show()
    print("Done!")
    return scores


def main(args):
    print(f"Evaluating for {args.data_path}")
    print("Loading data ...", end=' ')
    df = pd.read_csv(args.data_path)
    X = df.drop(["Date", "TeamA", "TeamB", "S", "Result"], axis=1)
    y = df["Result"]
    X_scaled = StandardScaler().fit_transform(X, y)
    print("Done!")

    models = [
        XGBClassifier(),
        RandomForestClassifier(),
        LogisticRegression(),
        LinearSVC(),
        DecisionTreeClassifier(),
        MLPClassifier(),
    ]

    print("Evaluating Models ...")
    data = []
    metrics = ("f1" ,"accuracy")
    for m in models:

        scores = custom_eval(m, X_scaled, y, display_cm=False, metrics=metrics)
        td = []
        for metric in metrics:
            td.append(scores[f'test_{metric}'].mean())
            td.append(scores[f'test_{metric}'].std())
        data.append([m.__class__.__name__] + td)

    df = pd.DataFrame(data, columns=["Model", "F1 Mean", "F1 Std Dev", "Accuracy Mean", "Accuracy Std Dev"])
    print(f"Done! Results -")
    print(df)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_path", type=str, required=True)
    args = parser.parse_args()

    main(args)
