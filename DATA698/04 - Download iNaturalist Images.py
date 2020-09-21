# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 07:15:13 2020

@author: Michael Silva
"""

import requests
from os import path, mkdir

base_url = "http://127.0.0.1:5000/"
has_work = True


def relay_image_downloaded(id):
    url = base_url + "image_downloaded?id=" + str(id)
    response = requests.get(url)
    response = response.json()
    if "success" not in response:
        print("Something bad happened > " + url)


while has_work:
    # Get a new job
    job = requests.get(base_url + "job")
    job = job.json()

    if job["id"] == "Done":
        has_work = False
    else:
        # Download the image
        img_url = job["img_url"]
        img_id = job["id"]
        img_id_str = str(img_id)
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
        relay_image_downloaded(img_id)
