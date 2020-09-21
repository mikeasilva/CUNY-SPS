# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 07:15:13 2020

@author: Michael Silva
"""

import requests
from os import path, mkdir
import json
import time

# Initial values
base_url = "http://127.0.0.1:5000/"
has_work = True
cooling_down = False
job_count = 0
starts_with = None

# How will this worker operate?  Which mode?
work_modes = {"1": "scrape_job", "2": "download_job", "3": "scrape_job", "4":"reset"}
work_mode = input("Enter work mode (1=scrape and download image, 2=download image ONLY, 3=scrape ONLY, 4=reset): ")
endpoint = work_modes[work_mode]
# Ask about label starting with
if work_mode in ["1", "3"]:
    starts_with = input("What should the label start with (Press enter for nothing)? ")
    if starts_with == "":
        starts_with = None

# Helper functions
def relay_image_downloaded(id):
    url = base_url + "image_downloaded?id=" + id
    response = requests.get(url)
    response = response.json()
    if "success" not in response:
        print("Something bad happened > " + url)

def get_img_path(label):
    img_path = "./iNaturalist/images/" + label + "/"
    # Create directories if needed
    if not path.exists(img_path):
        mkdir(img_path)
    return(img_path)

def download_image(img_url, img_path, img_id_str):
    # Check if image path exists
    file_extension = img_url.split(".")[-1].split("?")[0]
    file_path = img_path + img_id_str.zfill(8) + "." + file_extension
    if not path.exists(file_path):
        print("Downloading " + label + " >> " + img_url)
        img = requests.get(img_url)
        with open(file_path, "wb") as f:
            f.write(img.content)

# Main workflow loop
while has_work:
    if cooling_down:
        # We pulled data too fast so we need to let the API cool down
        print(
            "========> COMPLETED " + str(job_count) + " JOBS BEFORE COOL DOWN <========"
        )
        time.sleep(60)
        cooling_down = False
        job_count = 0

    if endpoint == work_modes["4"]:
        # Reset
        response = requests.get(base_url + "reset")
        print("Reset complete")
        has_work = False
    else:
        # Get a new job
        job_count += 1
        request_url = base_url + endpoint
        if starts_with is not None:
            request_url = request_url + "?starts_with=" + starts_with

        job = requests.get(request_url)
        job = job.json()

        if job["id"] == "Done":
            has_work = False

        if endpoint == work_modes["1"] and has_work:
            # Scrape observation data
            label = job["label"]
            print(label + " >> Scrapping " + job["url"])
            response = requests.get(job["url"])
            if response.status_code == 200:
                response_json = response.json()
                try:
                    img_url = response_json["results"][0]["photos"][0]["url"].replace(
                        "square", "large"
                    )
                    try:
                        lat = response_json["results"][0]["geojson"]["coordinates"][1]
                        lon = response_json["results"][0]["geojson"]["coordinates"][0]
                    except:
                        lat = None
                        lon = None
                    observed_on = response_json["results"][0]["observed_on"]
                    data = {
                        "img_url": img_url,
                        "lat": lat,
                        "lon": lon,
                        "observed_on": observed_on,
                        "scrapped": 1,
                    }
                except:
                    data = {"scrapped": 1, "error": 1}
                json_data = json.dumps(data)
                response = requests.post(
                    base_url + "image_data?id=" + str(job["id"]),
                    data=json_data,
                    headers={"Content-Type": "application/json"},
                )
                if work_mode == "1":
                    # Download the image too
                    img_id_str = str(job["id"])
                    img_path = get_img_path(label)
                    download_image(img_url, img_path, img_id_str)
                    relay_image_downloaded(img_id_str)
            else:
                cooling_down = True

        if work_mode == "2" and has_work:
            # Download the image ONLY
            img_url = job["img_url"]
            img_id_str = str(job["id"])
            label = job["label"]
            img_path = get_img_path(label)
            download_image(img_url, img_path, img_id_str)
            relay_image_downloaded(img_id_str)
