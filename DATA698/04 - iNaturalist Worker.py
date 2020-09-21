# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 07:15:13 2020

@author: Michael Silva
"""

import requests
from os import path, mkdir
import json
import time

base_url = "http://127.0.0.1:5000/"
has_work = True
cooling_down = False
job_count = 0
starts_with = None


work_modes = {"1": "scrape_job", "2": "download_job", "3": "reset"}
work_mode = input("Enter work mode (1=scrape, 2=download image, 3=reset): ")
endpoint = work_modes[work_mode]
if work_mode == "1":
    starts_with = input("What should the label start with (Press enter for nothing)? ")
    if starts_with == "":
        starts_with = None


def relay_image_downloaded(id):
    url = base_url + "image_downloaded?id=" + id
    response = requests.get(url)
    response = response.json()
    if "success" not in response:
        print("Something bad happened > " + url)


while has_work:
    if cooling_down:
        print(
            "========> COMPLETED " + str(job_count) + " JOBS BEFORE COOL DOWN <========"
        )
        time.sleep(60)
        cooling_down = False
        job_count = 0
    if endpoint == work_modes["3"]:
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
            print(job["label"] + " >> Scrapping " + job["url"])
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
            else:
                cooling_down = True
        if endpoint == work_modes["2"] and has_work:
            # Download the image
            img_url = job["img_url"]
            img_id_str = str(job["id"])
            label = job["label"]
            img_path = "./iNaturalist/images/" + label + "/"
            # Create directories if needed
            if not path.exists(img_path):
                mkdir(img_path)
            # Check if image path exists
            file_extension = img_url.split(".")[-1].split("?")[0]
            file_path = img_path + img_id_str.zfill(8) + "." + file_extension
            if not path.exists(file_path):
                print("Downloading " + label + " >> " + img_url)
                img = requests.get(img_url)
                with open(file_path, "wb") as f:
                    f.write(img.content)
            relay_image_downloaded(img_id_str)
