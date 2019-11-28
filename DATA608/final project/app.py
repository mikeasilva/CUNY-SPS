# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 08:52:11 2019

@author: Michael Silva
"""

import os
import csv
from flask import Flask, jsonify, request, send_file

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

@app.route("/")
def index():
    html = open(os.path.join(APP_ROOT, "webpage.html")).read()
    return html

@app.route("/arrow-menu-down-gray.svg")
def arrow_menu_down_gray():
    return send_file(os.path.join(APP_ROOT, "arrow-menu-down-gray.svg"), mimetype='image/svg+xml')

@app.route("/api/v1/all-data")
def all_data():
    json = {}
    data = csv.DictReader(open(os.path.join(APP_ROOT, "study_data.csv")))
    for row in data:
        json_data = json.get(row['geoid'], list())
        year = row['year']
        if int(year) > 2000:
            year = str(int(year)-4) + "-" + year[-2:]
        json_data.append({
            "label": year,
            "low_share": row["low_class"],
            "middle_share": row["middle_class"],
            "upper_share": row["upper_class"],
            "low_est": int(round(int(row["hh"]) * float(row["low_class"]), 0)),
            "middle_est": int(round(int(row["hh"]) * float(row["middle_class"]), 0)),
            "upper_est": int(round(int(row["hh"]) * float(row["upper_class"]), 0))
        })
        json[row['geoid']] = json_data
    return jsonify(json)

@app.route("/api/v1/options")
def options():
    seen = set();
    options = {}
    html = ""
    data = csv.DictReader(open(os.path.join(APP_ROOT, "study_data.csv")))
    for row in data:
        if row['geoid'] not in seen:
            selected = ""
            if row['geoid'] == "36001":
                selected = " selected"
            html = html + '<option value="' + row['geoid'] + '"' + selected + '>' + row['name'].replace(", New York", "") + '</option>\n'
            options[row['geoid']] = row['name'].replace(", New York", "")
            seen.add(row['geoid'])
    return html

if __name__ == "__main__":
    app.run(debug=True)