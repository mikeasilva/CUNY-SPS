# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 13:26:41 2018

@author: Michael Silva
"""

import urllib
import zipfile
import shutil
from dbfread import DBF
import sqlite3 as db
import requests
import asyncio
import time
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Source: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

start_time = time.time()

print('Setting up db')
db_name = "Monroe Real Property Data.db"
con = db.connect(db_name)
con.row_factory = lambda cursor, row: row[0]
c = con.cursor()
c.execute('DROP TABLE IF EXISTS `scraped_data`')
c.execute('CREATE TABLE `scraped_data` (`SWIS`, `SBL`, `url`,`html`)')
c.execute('DROP TABLE IF EXISTS `sales_data`')
c.execute('CREATE TABLE `sales_data` (`sale_date` DATE, `price` REAL, `SWIS`,`SBL`)')
c.execute('CREATE INDEX `sd` ON `sales_data` (`SWIS`, `SBL`);')
con.commit()

print("--- %s seconds ---" % (time.time() - start_time))

print('Getting the Monroe County Tax Parcels Centroids')
url = 'http://gis.ny.gov/gisdata/fileserver/?DSID=1300&file=Monroe-Tax-Parcels-Centroid-Points-SHP.zip'
zip_file_name = url.split('file=')[1]
dbf_file_name = 'Monroe_2017_Tax_Parcel_Centroid_Points_SHP.dbf'

with urllib.request.urlopen(url) as response, open(zip_file_name, 'wb') as out_file:
    shutil.copyfileobj(response, out_file)
with zipfile.ZipFile(zip_file_name) as zf:
    zf.extractall()
print("--- %s seconds ---" % (time.time() - start_time))

print('Building list of urls to scrape')
urls_to_scrape = list()
prop_info = list()

for record in DBF(dbf_file_name):
    try:
        if record['PROP_CLASS'][0] == '2':
            scrape_me = 'https://www.monroecounty.gov/etc/rp/report.php?a='+record['SWIS']+'-'+record['SBL']
            urls_to_scrape.append(scrape_me)
            prop_info.append(record)
    except IndexError:
        continue
print("--- %s seconds ---" % (time.time() - start_time))

# Save the property attributes to the property_info table
print('Saving Property Attributes')
prop_info = pd.DataFrame(prop_info)
prop_info = prop_info[['SWIS', 'SBL', 'MUNI_NAME', 'YR_BLT', 'SQ_FT', 'ACRES',
                       'SCH_NAME', 'SEWER_DESC', 'WATER_DESC' , 'UTIL_DESC',
                       'BLDG_DESC', 'HEAT_DESC', 'FUEL_DESC', 'SQFT_LIV',
                       'NBR_KITCHN', 'NBR_F_BATH', 'NBR_BEDRM', 'CALC_ACRES']]
prop_info.to_sql('property_info', con, if_exists = 'replace')
print("--- %s seconds ---" % (time.time() - start_time))

def scrape(url):
    print('Scraping ' + url)
    return requests.get(url)

async def scrape_all(urls_to_scrape):
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(
            None,
            scrape,
            url
        )
        for url in urls_to_scrape
    ]
    for response in await asyncio.gather(*futures):
        print('Saving ' + response.url)
        url = response.url
        url = url.replace('https://www.monroecounty.gov/etc/rp/report.php?a=', '')
        url = url.split('-')
        swis = url[0]
        sbl = url[1]
        c.execute('INSERT INTO `scraped_data` VALUES (?, ?, ?, ?)', (swis, sbl, response.url, response.content))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a', {'class': 'sale-link'}):
            data = re.sub('\s+',' ',link.text).split('-')
            data[0] = data[0].strip()
            data[0] = datetime.strptime(data[0], '%m/%d/%Y')
            data[0] = datetime.date(data[0])
            data[1] = int(data[1].strip().replace('$' , '').replace(',', ''))
            data.append(swis)
            data.append(sbl)
            data = tuple(data)
            c.execute('INSERT INTO `sales_data` VALUES (?, ?, ?, ?)', data)
        
"""
urls_to_scrape = ["https://www.monroecounty.gov/etc/rp/report.php?a=264489-15208000030120000000"]
"""
loop = asyncio.get_event_loop()
for urls in chunks(urls_to_scrape, 100):
    loop.run_until_complete(scrape_all(urls))
loop.close()

print("--- %s seconds ---" % (time.time() - start_time))

print('Finalizing database')
con.commit()
con.close()
print("--- %s seconds ---" % (time.time() - start_time))
