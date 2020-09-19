# -*- coding: utf-8 -*-
"""
Gather iNaturalist Image URLs

Created on Fri Sep 18 16:24:40 2020

@author: Michael Silva

Having previously gathered iNaturalist observation records, and saved them to
JSON files, this script processess the data and gets the URL for the image. All
data are stored in a SQLite database.
"""

import time
import json
import requests
from glob import glob
import sqlite3

# It may take more than one pass to gather the image URLs.  Set this to False
# if this is not the first run on the script.

create_tables = False
cool_down = False

conn = sqlite3.connect("images.db")
c = conn.cursor()

if create_tables:
    c.execute("DROP TABLE IF EXISTS images;")
    c.execute("DROP TABLE IF EXISTS json_file;")
    c.execute(
        "CREATE TABLE images (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT, url text, img_url TEXT, lat REAL, lon REAL, observed_on TEXT, assigned INTEGER DEFAULT 0, downloaded INTEGER DEFAULT 0);"
    )
    c.execute("CREATE INDEX IF NOT EXISTS idx_assigned ON images (assigned);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_downloaded ON images (downloaded);")
    c.execute("CREATE TABLE json_file (file_name TEXT);")
    conn.commit()

def gather(cool_down):
    for file in glob("./iNaturalist/json/*.json"):
        c.execute("SELECT COUNT(*) FROM json_file WHERE file_name = ?", (file,))
        result = c.fetchone()
        if result[0] == 0:
            label = file.split("\\")[1].split("-")[0]
            with open(file) as json_file:
                data = json.load(json_file)
                if "results" in data and not cool_down:
                    for result in data["results"]:
                        url = result["uri"].replace(
                            "https://www.inaturalist.org/",
                            "https://api.inaturalist.org/v1/",
                        )
                        print(label + " >> " + url)
                        c.execute("SELECT COUNT(*) FROM images WHERE url = ?", (url,))
                        r = c.fetchone()
                        if r[0] == 0:
                            response = requests.get(url)
                            if response.status_code == 200:
                                response_json = response.json()
        
                                img_url = response_json["results"][0]["photos"][0]["url"]
                                img_url = img_url.replace("square", "large")
                                
                                lat = response_json["results"][0]["geojson"]["coordinates"][
                                    1
                                ]
                                lon = response_json["results"][0]["geojson"]["coordinates"][
                                    0
                                ]
                                observed_on = response_json["results"][0]["observed_on"]
        
                                insert_data = (
                                    label,
                                    url,
                                    img_url,
                                    lat,
                                    lon,
                                    observed_on,
                                )
        
                                c.execute(
                                    "INSERT INTO images (label, url, img_url, lat, lon, observed_on) VALUES (?,?,?,?,?,?)",
                                    insert_data,
                                )
                                conn.commit()
                            else:
                                cool_down = True
                                return cool_down
            if not cool_down:
                c.execute("INSERT INTO json_file VALUES (?)", (file,))
                conn.commit()
    return cool_down

while True:
    if cool_down:
        print("Cooling Down...")
        time.sleep(60) # Pause for 1 minutes
        cool_down = False
    cool_down = gather(cool_down)

conn.commit()
conn.close()
