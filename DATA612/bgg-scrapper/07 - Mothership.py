import sqlite3
from flask import Flask, jsonify, request, g
import json

DATABASE = "games.db"


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


app = Flask(__name__)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    return ""


@app.route("/assignment_complete")
def assignment_complete():
    """Handles posted ratings data."""
    cur = get_db().cursor()
    item_id = request.args.get("id")
    cur.execute("UPDATE item SET scraped = 1 WHERE id = ?", (item_id,))
    db_save()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/next_assignment")
def latest():
    cur = get_db().cursor()
    cur.execute(
        "SELECT item.id, item.bgg_id, filter.id FROM item, (SELECT MIN(id) AS id FROM item WHERE assigned = 0) AS filter WHERE item.id = filter.id;"
    )
    try:
        assignment = cur.fetchall()[0]
        cur.execute("UPDATE item SET assigned = 1 WHERE id = ?", (assignment["id"],))
        db_save()
    except:
        # We have assigned all the games
        assignment = {"id": "Done", "bgg_id": "Done"}
    return jsonify(assignment)


@app.route("/user_id")
def user_id():
    """Look for User id by user_name.  If none is given, create the record and return the new id."""
    username = request.args.get("username")
    cur = get_db().cursor()
    cur.execute("SELECT id FROM user WHERE name = ? LIMIT ?", (username, 1))
    try:
        user = cur.fetchall()[0]
    except:
        cur.execute("INSERT INTO user (name) VALUES (?)", (username,))
        db_save()
        user_id = cur.lastrowid
        user = {"id": user_id}
    return jsonify(user)


@app.route("/data_intake", methods=["POST"])
def data_intake():
    """Handles posted ratings data."""
    cur = get_db().cursor()
    for item_id, user_id, rating, rating_tstamp in request.get_json()[0]:
        try:
            cur.execute(
                "INSERT INTO ratings (item_id, user_id, rating, rating_tstamp) VALUES (?, ?, ?, ?)",
                (item_id, user_id, rating, rating_tstamp),
            )
        except:
            continue
    db_save()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


if __name__ == "__main__":
    app.run(debug=False)
