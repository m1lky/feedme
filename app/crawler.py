import socks,socket
import requests
import sys, os, json
from time import sleep
import feedparser
from models import post as post_model
from models import source as source_model
from models import log as log_model
class crawler:
	current_site = None
	post = None
	source = None
	log = None
	def __init__(self, DBSOURCE):
		socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
		socket.socket = socks.socksocket
		self.post = post_model.post(DBSOURCE)
		self.source = source_model.source(DBSOURCE)
		self.log = log_model.log(DBSOURCE)
	
	def get_sources(self):
		return self.source.get_all()

	def crawl_posts(self, sources):
		for s in sources:
			self.current_site = s['url']
			response = self.__request_feed(s['url'])
			feed = feedparser.parse(response)
			entries = feed.entries
			# print(feed.version)
			if("atom" in feed.version):
				self.__parse_atom(entries)
			elif("rss" in feed.version):
				self.__parse_rss(entries)
			source_finished = {}
			source_finished['event'] = 'source_finished-'+self.current_site
			self.log.insert(source_finished)
			
			
	#Todo: add error handling for infinite loop
	def __request_feed(self, url):
		self.current_site = url
		response = False
		attempts = 0
		while(True):
			response = requests.get(url)
			if(response.status_code == 200 or attempts > 3):
				break
			sleep(3);
			attempts += 1
		return response.text
	def __parse_atom(self, entries):
		for e in entries:
			insertion = {}
			atom_data_map = {'description':'summary'}
			for c in self.post.columns:
				if(c in atom_data_map):
					insertion[c] = getattr(e, atom_data_map[c], False)
				else:
					insertion[c] = getattr(e, c, False)
			insertion['website'] = self.current_site
			insertion['feed_type'] = 'atom'
			try:
				self.post.insert(insertion)
			except Exception as ex:
				error_log = {}
				error_log['event'] = str(ex)
				error_log['description'] = 'insertion of post'+json.dumps(insertion)+' for website ' + self.current_site
				self.log.insert(error_log)

	def crawl_for_image(self, url):
		return "asdf"
	def __parse_rss(self, entries):
		for e in entries:
			insertion = {}
			for c in self.post.columns:
				insertion[c] = getattr(e, c, False)
			insertion['website'] = self.current_site
			insertion['feed_type'] = 'rss'
			try:
				self.post.insert(insertion)
			except Exception as ex:
				error_log = {}
				error_log['event'] = str(ex)
				error_log['description'] = 'insertion of post'+json.dumps(insertion)+' for website ' + self.current_site
				self.log.insert(error_log)
