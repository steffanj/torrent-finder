# torrent-finder
Python 3 script to find torrents on various search engines; to retrieve the info of search matches; and, optionally, to start downloads from these matches.

## How to use
When run as main script (directly in terminal), torrentFinder will ask you questions about the torrents that you wish to find. The script searches on multiple torrent search engines, scrapes relevant html code, parses the results, re-orders those results (based on file size, whether or not the search result contains the words 'proper' or 'repack', and number of seeds), and presents them to you in your terminal. You can choose which of the results will be downloaded (if any). 

An example for the free ['Zeitgeist Addendum' movie](http://www.zeitgeistmovie.com/) is shown in the GIF below.
![Example run](https://github.com/steffanj/torrent-finder/blob/master/images/example.gif "Example")

If you don't want to run the interactive main script, you can run 'results = torrentFinder.getResults(query)' on a string search query to retrieve a dictionary containing the following information of each search result: 
* source: source (search engine), string
* title: torrent title, string
* size: approx. file size including unit (MB, GB), string
* proper: True if the search result contains the words 'proper' or 'repack'; False otherwise, boolean
* seeds: number of seeds, integer
* age: age or post date as provided by search engine (raw), string
* magnet: magnet link, string
* torrent: link to .torrent file, string

## To do
- [ ] Test/make work on Apple and Ubuntu machines
- [ ] Include date or age information in a neat way in the results overview
- [ ] Give a warning if an update is available: updates might include fixes for broken search parameters or support for new search engines
- [ ] Make a simple GUI
