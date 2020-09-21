# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 07:15:13 2020

@author: Michael Silva
"""

import sqlite3
from flask import Flask, jsonify, request, g
import json
from collections import OrderedDict 

DATABASE = "images.db"
debug = False
app = Flask(__name__)


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db


def db_save():
    get_db().commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    return ""


@app.route("/image_downloaded")
def image_downloaded():
    cur = get_db().cursor()
    image_id = request.args.get("id")
    cur.execute(
        "UPDATE images SET assigned = 1, downloaded = 1 WHERE id = ?", (image_id,)
    )
    db_save()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/image_scrapped")
def image_scrapped():
    cur = get_db().cursor()
    image_id = request.args.get("id")
    cur.execute("UPDATE images SET scrapped = 1 WHERE id = ?", (image_id,))
    db_save()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/image_data", methods=["POST"])
def data_intake():
    cur = get_db().cursor()
    image_id = request.args.get("id")
    data = OrderedDict(request.get_json())
    val = tuple(data.values())
    sql = "UPDATE images SET "
    for k in data.keys():
        sql = sql + k + " = ?, "
    sql = sql[: len(sql) - 2] + " WHERE id = " + image_id + ";"
    
    try:
        cur.execute(sql, val)
        db_save()
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
    except:
        return json.dumps({"failure": True}), 200, {"ContentType": "application/json"}


@app.route("/download_job")
def job():
    cur = get_db().cursor()
    cur.execute(
        "SELECT images.* FROM images, (SELECT MIN(id) AS id FROM images WHERE assigned = 0 and img_url IS NOT NULL and error = 0) AS f WHERE images.id = f.id;"
    )
    try:
        task = cur.fetchall()[0]
        cur.execute("UPDATE images SET assigned = 1 WHERE id = ?", (task["id"],))
        db_save()
    except:
        # We have assigned all the images
        task = {"id": "Done"}
    return jsonify(task)


@app.route("/reset")
def reset():
    cur = get_db().cursor()
    cur.execute("UPDATE images SET assigned = 0 WHERE downloaded = 0")
    cur.execute("UPDATE images SET scrapped = 0 WHERE scrapped = -1")
    db_save()
    return "Success"


@app.route("/scrape_job")
def scrape_job():
    cur = get_db().cursor()
    starts_with = request.args.get("starts_with")
    if starts_with is None:
        cur.execute(
            "SELECT images.* FROM images, (SELECT MIN(id) AS id FROM images WHERE scrapped = 0 AND error = 0) AS f WHERE images.id = f.id;"
        )
    else:
        cur.execute(
            "SELECT images.* FROM images, (SELECT MIN(id) AS id FROM images WHERE scrapped = 0 AND error = 0 AND label LIKE '"
            + starts_with
            + "%') AS f WHERE images.id = f.id;"
        )

    try:
        task = cur.fetchall()[0]
        cur.execute("UPDATE images SET scrapped = -1 WHERE id = ?", (task["id"],))
        db_save()
    except:
        # We have assigned all the images
        task = {"id": "Done"}
    return jsonify(task)


if __name__ == "__main__":
    app.run(debug=debug)
