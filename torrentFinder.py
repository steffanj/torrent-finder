# -*- coding: utf-8 -*-
"""
torrentFinder
Python 3 script to find torrents on various search engines; to retrieve the 
info of search matches; and, optionally, to start downloads from these matches.

# How to use
When run as main script (directly in terminal), torrentFinder will ask you 
questions about the torrents that you wish to find. The script searches on 
multiple torrent search engines, scrapes relevant html code, parses the results, 
re-orders those results (based on file size, whether or not the search result 
contains the words 'proper' or 'repack', and number of seeds), and presents 
them to you in your terminal. You can choose which of the results will be 
downloaded (if any). 

An example for the free 'Zeitgeist Addendum' movie (www.zeitgeistmovie.com) 
is shown in \images\example.GIF.

If you don't want to run the interactive main script, you can run 
'results = torrentFinder.getResults(query)' on a string search query to 
retrieve a dictionary containing the following information of each search result: 
* source: source (search engine), string
* title: torrent title, string
* size: approx. file size in MB, integer
* proper: True if the search result contains the words 'proper' or 'repack'; False otherwise, boolean
* seeds: number of seeds, integer
* age: age or post date as provided by search engine (raw)
* magnet: magnet link
* torrent: link to .torrent file

# To do
- [ ] Test/make work on Apple and Ubuntu machines
- [ ] Include date or age information in a neat way in the results overview
- [ ] Give a warning if an update is available: updates might include fixes for 
      broken search parameters or support for new search engines
- [ ] Make a simple GUI
"""

def main():
    import os
    import soupStructures
    import pandas as pd

    # Load some torrent search engine parameters
    sites = soupStructures.loadSites()    
    print('Will search on the following torrent sites: ')
    for idx, site in enumerate(sites):
        print('{}. {}'.format(idx+1,site['name']))
    print('')
    
    stop_flag = False
    while stop_flag == False:
        # Ask for the search terms and process query/queries
        queries_processed = queryProcessing(input('What would you like to search for?\nSeparate multiple' 
                        ' search terms with a comma:\n').split(','))
        # Call the method to actually retrieve torrent info for each query
        for query in queries_processed:
            results = getResults(query)
            
            # The DataFrame might be too wide for pandas to print neatly by 
            # default, some settings have to be changed
            pd.set_option('display.expand_frame_repr', False)
            pd.set_option('display.max_colwidth', 100)
            print("Displaying results for query '{}':\n".format(query))
            print(results[['title','size','seeds','source']])
            
            # User can specify which torrent to download
            choice_dl = int(input("\nWhich torrent would you like to download?"
                                  "\nPress '0' to cancel download:\n"))
            if choice_dl == 0:
                print("\nDid not start a download for query '{}'\n".format(query))
            else:
                # Opening magnet link with default application on machine
                print("\nOpening '{}', {} MB in your default torrent application".format(
                        results['title'].loc[choice_dl], 
                        results['size'].loc[choice_dl]))
                os.startfile(results['magnet'].loc[choice_dl])
        print('Handled all queries.')
    
        # Ask if user wants to do another search
        if input('Would you like to specify a new search query? y/n: ').lower()!='y': 
            stop_flag = True
            print('Shutting down torrentFinder')
        
def getResults(query):  
    import requests
    import soupStructures
    from bs4 import BeautifulSoup
    import pandas as pd
    import numpy as np
    
    # Initialize parameters and empty pandas DataFrame for the results
    sites = soupStructures.loadSites()    
    results = pd.DataFrame(columns=['title','size','age','seeds','proper',
                                    'source','magnet','torrent'])
    
    for i in sites:
        # Initializing search query 
        site = i['name']
        search_url = i['search_url']
        search_url_suffix = i['search_url_suffix']
        q_s_r = i['query_space_replace']
        
        # Retrieving html files  
        req = requests.get(search_url+query.replace(' ',q_s_r)+search_url_suffix)
        c = req.content
        
        # Parsing html files
        soup = BeautifulSoup(c,"lxml")
        
        # Extract relevant html code
        tags = soupStructures.initResults(site, soup)
        
        # Parse relevant html code     
        except_cntr = 0
        for tag in tags:
            try:
                r_hol = soupStructures.parseResult(site, tag, query)
                results = results.append(r_hol, ignore_index=True)
            except:
                except_cntr += 1
        if except_cntr>0: print('{} possible search results could not be parsed'.format(except_cntr))
        
    
    # Sort values on (1) number of seeds and (2) whether the result contains 
    # the words 'proper' or 'repacked'
    results['seeds'] = pd.to_numeric(results['seeds'], downcast='integer')
    results.sort_values(['seeds', 'proper'], axis=0, ascending=[False,False], inplace=True)
    results['no.']=np.arange(1, results.shape[0]+1)
    results.set_index('no.',inplace=True)

    # Return the results DataFrame
    return results  

def queryProcessing(queries):
    # Users can specify multiple episodes to search for using the format
    # 'TVSHOW S01E01-05' or 'TVSHOW S01E01-E05' to search for episodes 1, 2, 3, 
    # 4 and 5 of season 1 of show TVSHOW
    import re
    queries = list(map(str.strip, queries))
    queries_processed = []
    for query in queries:
        # Check if query is in the format 'TVSHOW S01E01-05'
        if re.search('.+ s[0-9][0-9]e[0-9][0-9]-[0-9][0-9]', query, re.IGNORECASE):
            # Query base (TV show and season)
            base = re.findall('(.+ s[0-9][0-9]e)[0-9][0-9]-[0-9][0-9]', query, re.IGNORECASE)[0]
            # Episode numbers that mark the boundaries of our search (E01, E05)
            start_episode = int(re.findall('.+ s[0-9][0-9]e([0-9][0-9])-[0-9][0-9]', query, re.IGNORECASE)[0])
            end_episode = int(re.findall('.+ s[0-9][0-9]e[0-9][0-9]-([0-9][0-9])', query, re.IGNORECASE)[0])
            # For each episode, reconstruct valid query using base + suffix
            for episode in range(end_episode-start_episode):
                suffix = start_episode + episode
                if suffix < 10:
                    suffix = '0{}'.format(suffix)
                else: 
                    suffix = str(suffix)
                queries_processed.append(base+suffix)
                
        # Same as above but now for query in the format 'TVSHOW S01E01-E05'
        # The difference is in the 'E05' instead of '05'
        # Both search queries should lead to the same result        
        elif re.search('.+ s[0-9][0-9]e[0-9][0-9]-e[0-9][0-9]', query, re.IGNORECASE):
            base = re.findall('(.+ s[0-9][0-9]e)[0-9][0-9]-e[0-9][0-9]', query, re.IGNORECASE)[0]
            start_episode = int(re.findall('.+ s[0-9][0-9]e([0-9][0-9])-e[0-9][0-9]', query, re.IGNORECASE)[0])
            end_episode = int(re.findall('.+ s[0-9][0-9]e[0-9][0-9]-e([0-9][0-9])', query, re.IGNORECASE)[0])
            for episode in range(end_episode-start_episode):
                suffix = start_episode + episode
                if suffix < 10:
                    suffix = '0{}'.format(suffix)
                else: 
                    suffix = str(suffix)
                queries_processed.append(base+suffix)
        else:
            queries_processed.append(query)
    return queries_processed
 
if __name__=='__main__': main()