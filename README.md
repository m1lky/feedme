# feedme
This is a content aggregator utility for rss and atom feeds over a proxy
**IT IS VERY MUCH IN AN ALPHA STATE**
Currently, it is capable of:
1. Crawling a list of RSS feeds from sources.txt through a proxy (TOR), as well as downloading images
2. Store posts in a sqlite3 database
3. Pop a webserver up on `localhost:5000`
4. Display posts in a paginated feed

## Known Issues:
* Deleting a post with images will delete all images

## Getting set up:
```
pip3 install beautifulsoup4
pip3 install requests
pip3 install feedparser
```
Using the package manager of your choice, install TOR
E.G.
* `apt-get install tor`
* `brew install tor`

You may need to run the 2to3 conversion tool for python on the feedparser library (easily googled)


## Code Notes:
### Basic flow of control:
crawler.py is responsible for all crawling
1. run tor outside of feedme, and it will connect via port 9050 (tor's default port) 

2. run "python3 run.py" to run the flask server
3. go to localhost:5000 to see the server
4. import sources in the top left of the website will import sources from sources.txt
5. crawl will send an ajax request to crawl all the websites from the imported sources
6. prune will delete all posts that don't have a source, and all images that don't have a post

### Database schema:
each table is a class inherited from database.py
each table has a list of columns, and hashable columns
instead of an ID, a hash of hashable columns is used (prevents duplicates)
insert function is defined in database.py, and automatically sets all columns not pass in the dictionary to False, as well as adds a timestamp and hash
__init__.py is where all the routes are stored, this is basically the controller
### TODO:
*  segregate posts into categories
*  add live-suggestion for filter
* add stop_crawler function
* create semaphore for crawler
* Detect iframes and handle them so non-tor requests aren't made
* rename images when downloaded
