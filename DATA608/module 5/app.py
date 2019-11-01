# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 08:52:11 2019

@author: Michael Silva
"""

import os
import pandas as pd
from flask import Flask, jsonify, request

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def get_tree_list():
    soql_url = (
        "https://data.cityofnewyork.us/resource/nwxe-4ae8.json?"
        + "$select=spc_common,count(tree_id)"
        + "&$group=spc_common"
    ).replace(" ", "%20")
    temp = pd.read_json(soql_url).dropna()
    return temp.spc_common.tolist()


app = Flask(__name__)


@app.route("/")
def index():
    html = open(os.path.join(APP_ROOT, "js_in_webpage.html")).read()
    return html


@app.route("/api/v1/predict/<tree>")
def predict(tree):
    # Predict the Borough based on the probability the user is seeing a tree
    soql_url = (
        "https://data.cityofnewyork.us/resource/nwxe-4ae8.json?"
        + "$select=boroname,count(tree_id)"
        + "&$where=spc_common='"
        + tree
        + "'"
        + "&$group=boroname"
    ).replace(" ", "%20")
    # Get the data, sort it by tree count, and clean up the columns
    df = pd.read_json(soql_url).sort_values(by='count_tree_id', ascending=False).rename(columns={"count_tree_id": "n", "boroname": "Borough"})
    # Get the total number of trees
    total = df["n"].sum()
    # Compute the probability
    df['Probability'] = round(df['n'] / total, 2)
    # Get the first row (highest probability)
    df = df.drop(columns = ['n']).iloc[0]
    json = df.to_dict()
    # Fix The Bronx
    if json['Borough'] == "Bronx":
        json['Borough'] = "The Bronx"
    
    return jsonify(json)


@app.route("/api/v1/trees")
def trees():
    soql_url = (
        "https://data.cityofnewyork.us/resource/nwxe-4ae8.json?"
        + "$select=spc_common,count(tree_id)"
        + "&$group=spc_common"
    ).replace(" ", "%20")
    temp = pd.read_json(soql_url).dropna()
    trees = [{"label": i.title(), "key": i} for i in temp.spc_common.tolist()]
    return jsonify(trees)


if __name__ == "__main__":
    app.run(debug=True)
