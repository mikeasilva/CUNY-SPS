# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 07:15:13 2020

@author: Michael Silva
"""

import sqlite3
from flask import Flask, jsonify, request, g
import json

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


@app.route("/job")
def job():
    cur = get_db().cursor()
    cur.execute(
        "SELECT images.* FROM images, (SELECT MIN(id) AS id FROM images WHERE assigned = 0) AS f WHERE images.id = f.id;"
    )
    try:
        task = cur.fetchall()[0]
        cur.execute("UPDATE images SET assigned = 1 WHERE id = ?", (task["id"],))
        db_save()
    except:
        # We have assigned all the images
        task = {"id": "Done"}
    return jsonify(task)


@app.route("/image_downloaded")
def image_downloaded():
    cur = get_db().cursor()
    image_id = request.args.get("id")
    cur.execute(
        "UPDATE images SET assigned = 1, downloaded = 1 WHERE id = ?", (image_id,)
    )
    db_save()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


if __name__ == "__main__":
    app.run(debug=debug)
