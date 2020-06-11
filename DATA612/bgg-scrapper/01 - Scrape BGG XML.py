# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 21:36:38 2020

@author: Michael Silva
"""
import requests
from os.path import exists
from glob import glob
# Build up a list of files already scrapped
scrapped = set()
for prefix in ["./", "./skip/videogame/", "./skip/rpg/", "./skip/error/", "./scrapped/"]:
    for xml_file in glob(prefix + "*.xml"):
        xml_file = xml_file.split("\\")
        print(xml_file[-1])
        scrapped.add(xml_file[-1])

# Set this to True if you want to rescrape files
start_from_scratch = False

# Scrape until you hit this id
max_id = 298596
max_id = 1

for i in range(1, max_id + 1):
    xml_file = str(i) + ".xml"
    # Check to see if we need to scrape
    if xml_file not in scrapped or start_from_scratch:
        # This is the API endpoint
        url = "https://www.boardgamegeek.com/xmlapi/boardgame/" + str(i) + "?comments=1"
        response = requests.get(url)
        if response.status_code == 200:
            print("Writing " + xml_file)
            xml = response.text
            file = open(xml_file, "wb")
            file.write(xml.encode("UTF-8"))
            file.close()
    