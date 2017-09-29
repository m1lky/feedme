# feedme

In order to run:
pip3 install beautifulsoup4
pip3 install requests
pip3 install feedparser

you may need to run the 2to3 conversion tool for python on the feedparser library (easily googled)

Basic flow of control:
crawler.py is responsible for all crawling
run tor outside of feedme, and it will connect via port 9050
run "python3 run.py" to run the flask server
go to localhost:5000 to see the server
import sources in the top left of the website will import sources from sources.txt
crawl will send an ajax request to crawl all the websites from the imported sources

Database schema:
each table is a class inherited from database.py
each table has a list of columns, and hashable columns
instead of an ID, a hash of hashable columns is used (prevents duplicates)
insert function is defined in database.py, and automatically sets all columns not pass in the dictionary to False, as well as adds a timestamp and hash
__init__.py is where all the routes are stored, this is basically the controller
TODO:
segregate posts into categories
add "select2" minified to static folder
use select2 to filter post results based on:
  category of website
  website
add stop_crawler function
images:
  find images within feed responses
  store images in directory
  