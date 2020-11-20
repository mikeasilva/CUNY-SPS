# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 09:35:33 2020

@author: Michael
"""
import pandas as pd
import json

yolov3_cells = {250: 19, 500: 22, 1000: 25, 2000: 28}
yolov5_cells = {250: 14, 500: 17, 1000: 20, 2000: 23}
classes = ["Virginia Creeper", "Poison Ivy", "Brambles", "Box Elder"]

def extract_data_from_cell(cell, n_images, model):
    data = []
    for c in cell:
        if "text" in c:
            for line in c["text"]:
                if "image 1/1" in line:
                    img = line.split(":")[0].split("/")[-1]
                    found = {"Virginia Creeper":0, "Poison Ivy": 0, "Brambles":0, "Box Elder":0, "Null":0}
                    findings = line.split(":")[1]
                    for cl in classes:
                        if cl in findings:
                            found[cl] = 1
                    if len(findings.split(",")) == 1:
                        found["Null"] = 1
                    found["Image"] = img
                    found["n_images"] = n_images
                    found["Model"] = model
                    data.append(found)
    return data


def extract_data_from_yolov5_cell(cell):
    data = {}
    return data


# Process the YOLOv3 Results
with open('./results/YOLOv3 Field Tests Results.ipynb') as json_file:
    yolov3 = json.load(json_file)["cells"]
    


for n_images, key in yolov3_cells.items():
    cell = yolov3[key]["outputs"]
    data = extract_data_from_cell(cell, n_images, "YOLOv3")
    try:
        yolo_data = yolo_data + data.copy()
    except:
        yolo_data = data.copy()
    
    
# Process the YOLOv5 Results    
with open('./results/YOLOv5 Field Tests Results.ipynb') as json_file:
    yolov5 = json.load(json_file)["cells"]
    
for n_images, key in yolov5_cells.items():
    cell = yolov5[key]["outputs"]
    data = extract_data_from_cell(cell, n_images, "YOLOv5")
    yolo_data = yolo_data + data.copy()
    
    
df = pd.DataFrame(yolo_data)
df.to_csv("./report/field_test_results.csv", index = False)