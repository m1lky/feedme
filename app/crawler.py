import socks,socket
import requests
import sys, os, json, html
from urllib.parse import unquote
from bs4 import BeautifulSoup as bs
from time import sleep
from flask import url_for
import feedparser
from models import *
class crawler:
	current_source_hash = None
	current_site = None
	current_category = None
	post = None
	source = None
	log = None
	image = None
	#todo: allow custom port setting for tor
	def __init__(self):
		#set proxy to default tor port
		socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
		socket.socket = socks.socksocket
		self.post = post.post()
		self.source = source.source()
		self.log = log.log()
		self.image = image.image()
	
	def crawl_posts(self, sources):
		for s in sources:
			self.current_source_hash = s['hash']
			self.current_site = s['url']
			self.current_category = s['category']
			response = self.__request_feed(s['url'])
			if(response):
				feed = feedparser.parse(response)
				entries = feed.entries
				if("atom" in feed.version):
					id_hash = self.__parse_atom(entries)
				elif("rss" in feed.version):
					id_hash = self.__parse_rss(entries)
				self.__log('source_finished-'+self.current_site)
	# replaces img tags in content with a static path,
	# returns replaced content and array of images to be crawled
	def __replace_img_src_with_local_path(self, content):
		bs_response = bs(content, 'html.parser')
		return_images = []
		for i in bs_response.find_all('img'):
			src = i.get('src')
			#get last part of url for name of image file
			name = src.split('/')[-1]
			img = {}
			img['source_hash'] = self.current_source_hash
			img['remote_path'] = src # used for what url to crawl
			img['filename'] = unquote(name) # need to make sure it's not urlencoded
			return_images.append(img)
			i['src'] = url_for('static', filename='images/') + name
		return {'html':str(bs_response), 'images':return_images}

	# filthy error handling tries to connect 3 times
	# logs a failed response after 3 attempts
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
	#	parse atom for appropriate columns
	#		atom feeds are a lot less uniform,
	# 		so a dictionary is used to map atom to rss conventions for storage
	def __parse_atom(self, entries):
		for e in entries:
			insertion = {}
			atom_data_map = {'description':'summary', 'content':'content'}
			for c in self.post.columns:
				if(c in atom_data_map):
					if(c == 'description'):
						descr = getattr(e, atom_data_map[c], False)
						if(len(descr) > 250):
							soup = bs(descr, 'html.parser')
							insertion[c] = str(soup.p)
						else:
							insertion[c] = getattr(e, atom_data_map[c], False)
				else:
					if(c == 'content'):
						insertion[c] = self.get_content(e)
						self.__crawl_content_for_images(insertion[c])
					insertion[c] = getattr(e, c, False)
			insertion['feed_type'] = 'atom'
			id_hash = self.__insert_post(insertion)
			
	#returns content if possible, False otherwise
	def get_content(self, entry):
		content = getattr(entry, 'content', False)
		if(type(content) == list):
			return content[0].value
		elif(hasattr(content, 'value')):
			return content.value
		elif(content):
			return content
		s = getattr(entry,'summary_detail', False)
		if(hasattr(s, 'value')):
			return s.value
	# downloads a list of urls for images gathered from the src attribute in img tags
	# if the url is relative, it will attempt to append the current url to the src
	# writes images to disk in /app/static/images/
	def __crawl_images(self, urls, post_hash):
		for img in urls:
			self.__download_image(img['remote_path'], img['filename'] )
			del(img['remote_path'])
			img['post_hash'] = post_hash
			self.image.insert(img)
	# given a url to an image, downloads the image to app/static/images/
	# saves it as @param name
	def __download_image(self, url, name):
		s = self.attempt_request(url, True)
		with open('./app/static/images/'+name, 'wb') as fd:
			for chunk in s.iter_content(chunk_size=128):
				fd.write(chunk)

	#insert a post after it's been crawled by __parse_rss or __parse_atom
	def __insert_post(self, insertion):
		insertion['source_hash'] = self.current_source_hash
		insertion['category'] = self.current_category
		parsed_content = self.__replace_img_src_with_local_path(insertion['content'])
		insertion['content'] = parsed_content['html']
		parsed_description = self.__replace_img_src_with_local_path(insertion['description'])
		insertion['description'] = parsed_description['html']
		images = parsed_content['images'] + parsed_description['images']
		
		try:
			post_hash = self.post.insert(insertion)
			print(post_hash)
			self.__crawl_images(images, post_hash)
		except Exception as ex:
			print(ex)
			self.__log(str(ex), 'insertion of post'+json.dumps(insertion)+' for website ' + self.current_site)
			return False
	#parse rss for appropriate columns
	def __parse_rss(self, entries):
		for e in entries:
			insertion = {}
			for c in self.post.columns:
				if(c == 'content'):
					insertion[c] = self.get_content(e)
				else:
					insertion[c] = getattr(e, c, False)
			insertion['feed_type'] = 'rss'
			id_hash = self.__insert_post(insertion)


