"""
Tuning Random Forrest Clasifer and Logistic Regression and MLP
on combined match and player data with feature selection
Author: Atharv Sonwane
"""

import os
from pathlib import Path
import argparse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import optuna

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
from sklearn.feature_selection import VarianceThreshold



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
    print("Done!")

    X = df.drop(["Date", "TeamA", "TeamB", "S", "Result"], axis=1)
    y = df["Result"]
    X = StandardScaler().fit_transform(X, y)

    rf = RandomForestClassifier()
    lg = LogisticRegression()

    print("Evaluating with feature selection  ...")
    data = []
    metrics = ("f1" ,"accuracy")
    for m in [rf, lg]:
        X_transformed = SelectFromModel(estimator=m).fit_transform(X, y)
        scores = custom_eval(m, X_transformed, y, display_cm=False, metrics=metrics)
        td = []
        for metric in metrics:
            td.append(scores[f'test_{metric}'].mean())
            td.append(scores[f'test_{metric}'].std())
        data.append([m.__class__.__name__] + [X_transformed.shape[1]] + td)

    df = pd.DataFrame(data, columns=["Model", "Features Selected", "F1 Mean", "F1 Std Dev", "Accuracy Mean", "Accuracy Std Dev"])
    print(f"Done! Results -")
    print(df)

    print("Finding optimal number of features ...")
    data = {}
    metrics = ("f1" ,"accuracy")
    vals = list(range(10, 330, 50))
    for m in [rf, lg]:
        data[m.__class__.__name__] = {metric: [] for metric in metrics}
        for k in vals:
            print(k)
            X_transformed =  SelectKBest(k=k).fit_transform(X, y)
            scores = custom_eval(m, X_transformed, y, display_cm=False, metrics=metrics)
            for metric in metrics:
                data[m.__class__.__name__][metric].append(scores[f'test_{metric}'].mean())
        print(data)
        plt.figure(figsize=(10, 10))
        plt.title(m.__class__.__name__)
        for n, d in data[m.__class__.__name__].items():
            plt.plot(vals, d, label=n)
        plt.legend()
        plt.savefig(f"{m.__class__.__name__} F Nums.png")

    X_transformed = SelectKBest(k=60).fit_transform(X, y)
    def objective(trial):
        rf_max_depth = int(trial.suggest_loguniform('rf_max_depth', 2, 32))
        rf_n_estimators = int(trial.suggest_loguniform('rf_n_estimators', 50, 500))
        classifier_obj = RandomForestClassifier(max_depth=rf_max_depth, n_estimators=rf_n_estimators)
        score = cross_validate(classifier_obj, X_transformed, y, cv=StratifiedKFold(), scoring="accuracy")
        return score["test_score"].mean()

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_path", type=str, required=True)
    args = parser.parse_args()

    main(args)

