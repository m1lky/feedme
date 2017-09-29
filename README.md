# feedme

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
  
possible issues:
  concurrency with sqlite:
      description:
        can't seem to crawl and view posts at the same time
      solutions:
        switch to tinydb
        pause crawl insertion while attempting to read posts
        load all posts into a file before crawling
