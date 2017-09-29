import socks,socket
import requests
import sys, os, json, html
from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs
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
	def __init__(self):
		socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
		socket.socket = socks.socksocket
		self.post = post_model.post()
		self.source = source_model.source()
		self.log = log_model.log()
	
	def get_sources(self):
		return self.source.get_all()

	def crawl_posts(self, sources):
		for s in sources:
			self.current_site = s['url']
			response = self.__request_feed(s['url'])
			if(response):
				feed = feedparser.parse(response)
				entries = feed.entries
				if("atom" in feed.version):
					self.__parse_atom(entries)
				elif("rss" in feed.version):
					self.__parse_rss(entries)
				self.__crawl_response_for_images(response)
				self.__log('source_finished-'+self.current_site)

	#TODO: save response so that image paths are locally what they should be, instead of
	#what they are on the crawled server
	
	def __crawl_response_for_images(self, response):
		bs_response = bs(html.unescape(response), 'html.parser')
		image_tags = bs_response.find_all('img')
		for i in image_tags:
			src = i.get('src')
			#get last part of url for name of image file
			name = src.split('/')[-1]
			if('http' in src):
				s = self.attempt_request(src, True)
			else:
				parsed = urlparse(self.current_site)
				domain = parsed.scheme + '://' + parsed.netloc + '/'
				s = self.attempt_request(domain + src, True)
			with open('./app/static/images/'+name, 'wb') as fd:
				for chunk in s.iter_content(chunk_size=128):
					fd.write(chunk)
	
	def attempt_request(self, url, stream_flag = False):
		attempts = 1
		while(True):
			response = requests.get(url, stream=stream_flag)
			if(response.status_code == 200):
				return response
			if(attempts > 4):
				self.__log('failed_request-'+url, 'attempted '+str(attempts)+' times')
			sleep(3);
			attempts += 1
		return False
	def __log(self, event, description = False):
		log = {}
		log['event'] = event
		log['description'] = description
		self.log.insert(log)
	def __request_feed(self, url):
		return self.attempt_request(url).text
	#parse atom for appropriate columns
	def __parse_atom(self, entries):
		for e in entries:
			insertion = {}
			atom_data_map = {'description':'summary', 'content':'content'}
			for c in self.post.columns:
				if(c in atom_data_map):
					if(c == 'content'):
						insertion[c] = getattr(e, atom_data_map[c], False)[0].value
					elif(c == 'description'):
						descr = getattr(e, atom_data_map[c], False)
						if(len(descr) > 250):
							soup = bs(descr, 'html.parser')
							insertion[c] = str(soup.p)
						else:
							insertion[c] = getattr(e, atom_data_map[c], False)
				else:
					insertion[c] = getattr(e, c, False)
			insertion['website'] = self.current_site
			insertion['feed_type'] = 'atom'
			try:
				self.post.insert(insertion)
			except Exception as ex:
				self.__log(str(ex), 'insertion of post'+json.dumps(insertion)+' for website ' + self.current_site)
				

	
	#parse rss for appropriate columns
	def __parse_rss(self, entries):
		for e in entries:
			insertion = {}
			for c in self.post.columns:
				if(c == 'content'):
					insertion[c] = getattr(e, c, False)[0].value		
				else:
					insertion[c] = getattr(e, c, False)
			insertion['website'] = self.current_site
			insertion['feed_type'] = 'rss'
			try:
				self.post.insert(insertion)
			except Exception as ex:
				self.__log(str(ex), 'insertion of post'+json.dumps(insertion)+' for website ' + self.current_site)

