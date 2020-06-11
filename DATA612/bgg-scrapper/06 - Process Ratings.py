# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 13:08:26 2020

@author: Michael
"""
import json
from glob import glob
import sqlite3
import html

create_db = True
create_bgg_index = False

def get_item_id(bgg_id, cur):
	cur.execute("SELECT * FROM item WHERE bgg_id = ? LIMIT ?", (bgg_id, 1))
	row = cur.fetchone()
	return row[0]

def extract_ratings(json_file, cur):
	count = 0
	with open(json_file, encoding="utf8") as f:
			data = json.load(f)
			for i in data['items']:
				rating = i['rating']
				rating_tstamp = i['rating_tstamp']
				try:
					user_name = i['user']['username']
					cur.execute("SELECT * FROM user WHERE name = ? LIMIT ?", (user_name, 1))
					try:
						user_id = cur.fetchone()[0]
					except:
						cur.execute('INSERT INTO user (name) VALUES (?)', (user_name,))
						conn.commit()
						user_id = cur.lastrowid
					# Add in the ratings
					try:
						cur.execute('INSERT INTO ratings (item_id, user_id, rating, rating_tstamp) VALUES (?, ?, ?, ?)', (item_id, user_id, rating, rating_tstamp))
					except:
						continue
					count += 1
				except:
					continue
	return count

def check_off(item_id, cur):
	cur.execute("UPDATE item SET assigned = 1 AND scraped = 1 WHERE id = "+str(item_id))
	conn.commit()

def process_xml(xml_file):
	bgg_id = xml_file.split(".xml")[0].split("\\")[-1]
	cur.execute("SELECT * FROM item WHERE bgg_id = ? LIMIT ?", (bgg_id, 1))
	row = cur.fetchone()
	if row is None:
		found_line = False
		xml = open(xml_file, "r",  encoding="utf8") 
		while not found_line:
			line = xml.readline()
			if '<name primary="true"' in line:
				name = html.unescape(line.split("</name>")[0].split(">")[1])
				cur.execute('INSERT INTO item (name, bgg_id) VALUES (?, ?)', (name, bgg_id))
				found_line = True
		xml.close()

# Let's Get Started!!
conn = sqlite3.connect('games.db')
cur = conn.cursor()

if create_db:
	# Create the database
	cur.execute('''CREATE TABLE IF NOT EXISTS "item" (
		"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
		"name"	TEXT,
		"bgg_id"	INTEGER UNIQUE,
		"assigned"	INTEGER DEFAULT 0,
		"scraped"	INTEGER DEFAULT 0
	);''')

	cur.execute('''CREATE TABLE IF NOT EXISTS "user" (
		"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
		"name"	TEXT
	);''')

	cur.execute('''CREATE TABLE IF NOT EXISTS "ratings" (
		"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
		"item_id"	INTEGER,
		"user_id"	INTEGER,
		"rating"	INTEGER,
		"rating_tstamp"	TEXT
	);''')

	cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_ratings ON ratings (item_id, user_id);''')
	cur.execute('''CREATE INDEX IF NOT EXISTS user_name ON user (name);''')
	cur.execute('''CREATE INDEX IF NOT EXISTS idx_assigned ON item (assigned);''')
	conn.commit()

if create_bgg_index:
	limit = 100
	print("Creating BGG Index...")
	print(" Processing scrapped items...")
	count = 0
	for xml_file in glob("./scrapped/*.xml"):
		process_xml(xml_file)
		count += 1
		if count > limit:
			conn.commit()
			count = 0
	print(" Processing non-scrapped items...")
	count = 0
	for xml_file in glob("./*.xml"):
		process_xml(xml_file)
		count += 1
		if count > limit:
			conn.commit()
			count = 0
"""

print("Getting scraped list...")
cur.execute("SELECT bgg_id FROM item WHERE scraped = 1")
scraped_bgg_ids = list()
for row in cur:
	 scraped_bgg_ids.append(row[0])
print(" There are "+str(len(scraped_bgg_ids))+" games that have been scraped!")


print("Building workload...")
workload = dict()
lookup = dict()

for json_file in glob("./ratings/*.json"):
	f = json_file.split("\\")[1]
	bgg_id = f.split("_")[0]
	# Get the item_id for this game
	item_id = lookup.get(bgg_id, None)
	if item_id is None:
		item_id = get_item_id(bgg_id, cur)
		lookup[bgg_id] = item_id
	# Add the json file to the workload
	w = workload.get(item_id, list())
	w.append(json_file)
	workload[item_id] = w

print("Processing ratings...")
processed = 0
for item_id, json_files in workload.items():
	count = 0
	for json_file in json_files:
		f = json_file.split("\\")[1]
		bgg_id = f.split("_")[0]
		count += extract_ratings(json_file, cur)
	print(" Added " + str(count) + " ratings for " + bgg_id)
	check_off(item_id, cur)
	processed += 1
	print(str(processed)+" out of "+str(len(workload))+" games")
"""
conn.commit()
cur.close()
print("Done!")