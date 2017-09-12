import socks,socket
import requests
import sys, os
from time import sleep
import feedparser

sys.path.insert(1, os.path.join(sys.path[0], '../models/'))
from post import post
from source import source
class crawler:
	current_site = None
	post = None
	source = None
	def __init__(self):
		socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
		socket.socket = socks.socksocket
		self.post = post()
		self.source = source()
	
	def get_sources(self):
		return self.source.get_all()

	def get_posts(self, sources):
		for s in self.get_sources():
			response = self.__request_feed(feed)
			self.__parse_feed(response)
	#Todo: add error handling for infinite loop
	def __request_feed(self, url):
		self.current_site = url
		response = False
		while(True):
			response = requests.get(url)
			if(response.status_code == 200):
				break
			sleep(5);
		return response.text
	def __parse_feed(self, response):
		feed = feedparser.parse(response)
		entries = feed.entries
		for e in entries:
			try:
				self.post.insert(e.title, e.link, e.description, self.current_site)
			except AttributeError as error:
				print("Something wrong with the post entry: " + str(error))

#TODO: add categories to posts, not just sources

# s = source()
# print(s.import_sources('../static/sources.txt'))

c = crawler()
c.get_posts()
# p = post()
# print(p.get_posts())