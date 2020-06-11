# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 21:46:30 2020

@author: Michael Silva
"""
from bs4 import BeautifulSoup
from glob import glob
import requests

users_href = set()

html_files = glob("./user_index/*.html")

for html_file in html_files:
    #print(html_file)
    with open(html_file, "r", encoding="utf8") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, "lxml")
        forum_table = soup.findAll("table", {"class": "forum_table"})[0]
        for a in forum_table.findAll("a", href=True):
            if '/user/' in a['href']:
                users_href.add(a['href'])

print(len(users_href))
            
"""
move_to = "./skip/"
move_it_tags = {"<videogame>": "videogame/", "<rpg>": "rpg/", "<error>":"error/"}

for xml_file in xml_files:
    print(xml_file)
    move_it = False
    for line in open(xml_file, encoding="utf-8"):
        line = line.rstrip()
        tags = re.findall('<.*?>', line)
        for tag in tags:
            tag = tag.split(" ")[0] + ">"
            tag = tag.replace("/", "")
            tag = tag.replace(">>", ">")
            if tag in move_it_tags.keys():
                move_it = True
                move_it_to = move_to + move_it_tags[tag]
    if move_it:
        shutil.move(xml_file, move_it_to + xml_file)

            #xml_tags.add(tag)
       
with open('tags.txt', 'a') as the_file:
    for x in sorted(xml_tags):
        the_file.write(x+"\n")
        #print(x)
"""