# -*- coding: utf-8 -*-
"""
Supporting file for torrentFinder.py. Some elements were moved from 
torrentFinder.py to this file so that most feature updates will apply on 
this file only.
"""
import re
import requests
from bs4 import BeautifulSoup

def loadSites():
    # Load some parameters to use with the torrent search engines
    sites = [
    {'name':'EZTV', 
    'search_url':'https://eztv.ag/search/', 
    'query_space_replace':'-',
    'search_url_suffix':''
    },
     {'name':'1337X',
    'search_url':'https://1337x.to/search/',
    'query_space_replace':'+',
    'search_url_suffix':'/1/'
    }]
    
    return sites

def initResults(site, soup):
    # Extract html snippets that are relevant to the search query
    if site == 'EZTV':
        tags = soup.find_all("tr", class_='forum_header_border')
        return tags
    elif site == '1337X':
        tags = soup.find_all("tr")[1:]
        return tags
    else:
        print('No results were initialized')
        
def parseResult(site, tag, query):
    # Forward html snippets that are to be parsed to the correct method; 
    # each search engine has his own method
    if site == 'EZTV':
        result = EZTV(site, tag, query)
        return result
    elif site == '1337X':
        result = LEETX(site, tag, query)
        return result
    
def EZTV(site, tag, query):
    # Parse EZTV search results
    if isRelevant(query, tag.contents[3].a.text):
        result = {
            'title':tag.contents[3].a.text,
            'magnet':tag.contents[5].find_all(class_="magnet")[0]["href"],
            'torrent':tag.contents[5].find_all(class_="download_1")[0]["href"],
            'size':int(float(tag.contents[7].text.split(' ')[0])),
            'age':tag.contents[9].text,
            'seeds':int(tag.contents[11].text),
            'source':site,
            'proper':isProper(tag.contents[3].a.text)
                        }
        return result
    else:
        return None
		
def LEETX(site, tag, query):
    # Parse 1337X search results
    if isRelevant(query, tag.contents[1].text):
        result = {
            'title':tag.contents[1].text,
            'size':int(float(tag.contents[9].text.split(' ')[0])),
            'age':tag.contents[7].text,
            'seeds':int(tag.contents[3].text),
            'source':site,
            'proper':isProper(tag.contents[1].text)
            }
        # The search results link to a separate pages that contain the magnet
        # and torrent links, so these have to be opened and parsed as well
        base_url = 'https://1337x.to'
        download_url = tag.contents[1].find_all("a")[1]["href"]
        req_tmp = requests.get(base_url+download_url)
        c_tmp = req_tmp.content
        soup_tmp = BeautifulSoup(c_tmp, "lxml")
        magnet_str = str(soup_tmp.find_all(class_='download-links')[0].contents[1])
        torrent_str = str(soup_tmp.find_all(class_='download-links')[0])
        result['magnet'] = re.findall('.*href="(.*)" onclick', magnet_str)[0]
        result['torrent'] = re.findall('.*href="(.*torrent)"', torrent_str)[0]
        return result
    else:
        return None

def isProper(tag_text):
    # Check if the description of a search result contains the words 'proper' 
    # or 'repack'
    if re.search('[^a-z]*proper[^a-z]*', tag_text, re.IGNORECASE):
        return True
    elif re.search('[^a-z]*repack[^a-z]*', tag_text, re.IGNORECASE):
        return True
    else:
        return False

def isRelevant(query, tag):
    query_parts = query.split()
    relevant = True
    for part in query_parts:
        if not re.search(part, tag, re.IGNORECASE): 
            relevant = False
            break
    return relevant
        
                        
                    
    