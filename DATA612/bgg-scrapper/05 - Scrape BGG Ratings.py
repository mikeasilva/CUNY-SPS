# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 21:36:38 2020

@author: Michael Silva
"""
import json
import requests
from os.path import exists
from glob import glob
from shutil import move
import time


# Build up a list of files already scrapped
scrapped = set()
"""
for json_file in glob("./ratings/*.json"):
    json_file = json_file.split("\\")[-1]
    scrapped.add(json_file)
"""

def scrape_and_save(object_id, page_id, json_file):
    url = "https://api.geekdo.com/api/collections?ajax=1&objectid="+(object_id)+"&objecttype=thing&oneperuser=1&pageid="+str(page_id)+"&require_review=true&showcount=50&sort=rating&require_rating=true"
    response = requests.get(url)
    j = response.json()
    if "errors" in j.keys():
        return "errors"
    elif "items" not in j.keys():
        return "no items"
    elif len(j['items']) < 1:
        return "no items"
    else:
        json_ratings = response.text
        file = open("./ratings/" + json_file, "wb")
        file.write(json_ratings.encode("UTF-8"))
        file.close()
        return "data"


for xml_file in glob("*.xml"):
    i = xml_file.split(".")[0]
    keep_scraping_ratings = True
    page_id = 0
    print("Scraping "+str(i)+" ratings")
    retry = False
    while keep_scraping_ratings:
        if not retry:
            page_id += 1
        json_file = str(i) + "_" + str(page_id) + ".json"
        #if json_file not in scrapped:
        if not exists("./ratings/"+json_file):
            results = scrape_and_save(i, page_id, json_file)
            if results == "errors":
                print(" API throwing errors. Pausing the scrapping...")
                retry = True
                time.sleep(30)
            elif results == "no items":
                print(" Done Scrapping")
                keep_scraping_ratings = False
                retry = False
                move(xml_file, "./scrapped/" + xml_file)
            else:
                print (" Scrapped "+str(page_id))
                retry = False
"""
from os import remove

for json_file in glob("./ratings/*.json"):
    with open(json_file) as f:
        j = json.load(f)
        delete_me = False
        if "items" not in j.keys():
            delete_me = True
        elif len(j['items']) < 1:
            delete_me = True
        if delete_me:
            remove(json_file)
"""