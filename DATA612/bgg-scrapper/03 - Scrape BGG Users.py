# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 21:36:38 2020

@author: Michael Silva
"""
from bs4 import BeautifulSoup
import requests
import grequests
from glob import glob
from concurrent.futures import ProcessPoolExecutor, as_completed

scrapped = set()


def save_soup(soup, i):
    html = soup.prettify()
    file = open("./user_index/" + str(i) + ".html", "wb")
    file.write(html.encode("UTF-8"))
    file.close()


def download_and_save(url):
    i = url.split("?")[0].split("/")[-1]
    print(str(i) + ".html")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    save_soup(soup, i)
    return 1

# Build up a list of the pages index pages already scrapped
for html_file in glob("./user_index/*.html"):
    html_file = html_file.split("\\")
    scrapped.add(html_file[-1])

# https://www.boardgamegeek.com/users?country=&state=&city=
response = requests.get("https://www.boardgamegeek.com/users/page/1?country=&state=&city=")
soup = BeautifulSoup(response.text, "lxml")
if "1.html" not in scrapped:
    save_soup(soup, 1)

for a in soup.find_all('a'):
    if "last page" in str(a):
        a_text = a.text
        last_page = int(a_text.replace("[", "").replace("]", ""))

# Build a list of URLs to scrape
URLs = []
for i in range(2, last_page + 1):
    html_file = str(i) + ".html"
    if html_file not in scrapped:
        URLs.append("https://www.boardgamegeek.com/users/page/" + str(i) + "?country=&state=&city=")

reqs = (grequests.get(link) for link in URLs)
resp = grequests.imap(reqs, grequests.Pool(10))
for r in resp:
    url = r.url
    i = url.split("?")[0].split("/")[-1]
    soup = BeautifulSoup(r.text, "lxml")
    save_soup(soup, i)

"""
with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [ executor.submit(download_and_save, url) for url in URLs ]
    results = 0
    for result in as_completed(futures):
        results + 1
"""

"""
for i in range(2, last_page + 1):
    html_file = str(i) + ".html"
    if html_file not in scrapped:
        print(str(i) + " of " + str(last_page))
        response = requests.get("https://www.boardgamegeek.com/users/page/" + str(i) + "?country=&state=&city=")
        soup = BeautifulSoup(response.text, "lxml")
        save_soup(soup, i)


# https://www.boardgamegeek.com/geekcollection.php?ajax=1&action=collectionpage&username=zombiegod&userid=3130&gallery=&sort=title&sortdir=&page=&pageID=2&ff=1&hiddencolumns=&publisherid=&searchstr=&rankobjecttype=subtype&rankobjectid=1&columns[]=title&columns[]=status&columns[]=version&columns[]=rating&columns[]=bggrating&columns[]=plays&columns[]=comment&columns[]=commands&minrating=&rating=&minbggrating=&bggrating=&minplays=&maxplays=&searchfield=title&geekranks=Board%20Game%20Rank&subtype=boardgame&excludesubtype=&own=both&trade=both&want=both&wanttobuy=both&prevowned=both&comment=both&wishlist=both&rated=1&played=both&wanttoplay=both&preordered=both&hasparts=both&wantparts=both&wishlistpriority=
"""