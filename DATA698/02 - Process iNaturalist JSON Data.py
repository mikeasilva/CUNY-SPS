# -*- coding: utf-8 -*-
"""
Process iNaturalist JSON Data

Created on Fri Sep 18 16:24:40 2020

@author: Michael Silva

Having previously gathered iNaturalist observation records, and saved them to
JSON files, this script processess the data and builds out an index of API calls.
All data will be stored in a SQLite database.
"""

import json
from glob import glob
import sqlite3

create_tables = False

conn = sqlite3.connect("images.db")
c = conn.cursor()

if create_tables:
    c.execute("DROP TABLE IF EXISTS image;")
    c.execute("DROP TABLE IF EXISTS json_file;")
    c.execute(
        "CREATE TABLE images (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT, url text, img_url TEXT DEFAULT NULL, lat REAL DEFAULT NULL, lon REAL DEFAULT NULL, observed_on TEXT DEFAULT NULL, scrapped INTEGER default 0, assigned INTEGER DEFAULT 0, downloaded INTEGER DEFAULT 0, error INTEGER DEFAULT 0);"
    )
    c.execute("CREATE INDEX IF NOT EXISTS idx_assigned ON images (assigned);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_downloaded ON images (downloaded);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_scrapped ON images (scrapped);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_error ON images (error);")
    c.execute("CREATE TABLE json_file (file_name TEXT);")
    conn.commit()

for file in glob("./iNaturalist/json/*.json"):
        c.execute("SELECT COUNT(*) FROM json_file WHERE file_name = ?", (file,))
        result = c.fetchone()
        if result[0] == 0:
            print(file)
            with open(file) as json_file:
                label = file.split("\\")[1].split("-")[0]
                data = json.load(json_file)
                if "results" in data:
                    for result in data["results"]:
                        if "inaturalist.org" in result["uri"]:
                            url = result["uri"].replace(
                                "https://www.inaturalist.org/",
                                "https://api.inaturalist.org/v1/",
                            ).replace(
                                "http://www.inaturalist.org/",
                                "https://api.inaturalist.org/v1/",
                            )
                            c.execute("SELECT COUNT(*) FROM images WHERE url = ?", (url,))
                            r = c.fetchone()
                            if r[0] == 0:
                                c.execute("INSERT INTO images (label, url) VALUES (?,?);", (label, url))
            c.execute("INSERT INTO json_file VALUES (?)", (file,))
            conn.commit()

conn.close()
