# -*- coding: utf-8 -*-
"""
Gather iNaturalist JSON Data

Created on Tue Sep 15 20:23:39 2020

@author: Michael Silva

This script gathers data on iNaturalist observations.  The data are organized
by iNaturalist taxons.  It will request the maximum allowed number of data and
save them as JSON files for further processing.
"""

from os import path
import json
import requests

# iNaturalist Taxon ID and the Label (does not have to be unique)
taxon_id_and_label = {
    "58732": "Poison Ivy",
    "58729": "Poison Ivy",
    "50278": "Virginia Creeper",
    "47726": "Box Elder",
    "138680": "Thicket Bean",
    "62671": "Kudzu",
    "62666": "Kudzu",
    "82529": "Grapevine",
    "119936": "Grapevine",
    "50625": "Hoptree",
    "58738": "Sumac",
    "55911": "Bramble",
    "54436": "Bramble",
    "47544": "Bramble",
    "125489": "Bramble",
    "50298": "Strawberry",
    "243824": "Strawberry",
    "77835": "Japanese Honeysuckle",
    "50310": "Jack in the Pulpit",
    "166162": "Boston Ivy",
    "129021": "Honewort",
    "51435": "Trillium",
    "50855": "Trillium",
    "51741": "Goutweed",
    "85485": "Hog Peanut",
}
# Number of observations per API call
per_page = 100
# iNaturalist currently only allows 10,000 results
inaturalist_max = int(round(10000 / per_page, 0))


for taxon_id, label in taxon_id_and_label.items():
    print("Gathering " + taxon_id_and_label[taxon_id] + " Data...")
    scrape_and_save = True
    page = 1

    while scrape_and_save:
        # Determine if this has already been scrapped
        page_str = str(page)
        page_str = page_str.zfill(3)
        file_path = (
            "./iNaturalist/json/"
            + taxon_id_and_label[taxon_id]
            + "-"
            + taxon_id
            + "-"
            + page_str
            + ".json"
        )
        if not path.isfile(file_path):
            # File does not exist so scrape and save
            url = (
                "https://api.inaturalist.org/v1/observations?verifiable=true&order_by=observations.id&order=desc&page="
                + str(page)
                + "&spam=false&taxon_id="
                + taxon_id
                + "&locale=en-US&preferred_place_id=1&per_page="
                + str(per_page)
                + "&return_bounds=true&quality_grade=research"
            )
            response = requests.get(url)
            response_json = response.json()

            # Save the JSON data
            with open(file_path, "w") as f:
                json.dump(response_json, f)
        # Determine how much there is to scrape
        if "pages_to_scrape" not in locals():
            with open(file_path) as f:
                response_json = json.load(f)
            pages_to_scrape = int(round(response_json["total_results"] / per_page, 0))
            if pages_to_scrape > inaturalist_max:
                pages_to_scrape = inaturalist_max

        print("  " + str(page) + " of " + str(pages_to_scrape))
        # Check if we have more to scrape
        if page == pages_to_scrape or page > pages_to_scrape:
            scrape_and_save = False
            del pages_to_scrape
        else:
            page += 1

