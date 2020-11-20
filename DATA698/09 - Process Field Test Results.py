# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 09:35:33 2020

@author: Michael
"""

import json

yolov3_cells = {250: 19, 500: 22, 1000: 25, 2000: 28}
yolov5_cells = {250: 14, 500: 17, 1000: 20, 2000: 23}


# Process the YOLOv3 Results
with open('./results/YOLOv3 Field Tests Results.ipynb') as json_file:
    yolov3 = json.load(json_file)["cells"]
    
for n_images, key in yolov3_cells.items():
    cell = yolov3[key]["outputs"]
    print(n_images)
    
    
# Process the YOLOv5 Results    
with open('./results/YOLOv5 Field Tests Results.ipynb') as json_file:
    yolov5 = json.load(json_file)["cells"]
    
for n_images, key in yolov5_cells.items():
    cell = yolov5[key]["outputs"]
    print(n_images)