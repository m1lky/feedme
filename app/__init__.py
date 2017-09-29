#imports
import sys, datetime
from urllib.parse import urlparse
sys.path.append('./app')
sys.path.append('app/static')
from .models import post as post_model
from .models import source as source_model
from crawler import crawler
from flask import Flask, render_template, redirect
import config

#configs
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
app = Flask(__name__)
@app.template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
	date_format = '%-I:%M %p, %b %-d, %Y'
	if(type(date) == int):
		formatted = datetime.datetime.fromtimestamp(
			date
		).strftime(date_format)
		return formatted
	elif(type(date) == str):
		if(is_number(date[:4])):
			return datetime.datetime.strptime( date,"%Y-%m-%dT%H:%M:%SZ" ).strftime(date_format)
		else:
			return datetime.datetime.strptime( date,"%a, %d %b %Y %H:%M:%S %z" ).strftime(date_format)
@app.template_filter('website')
def _jinja2_filter_website(website, fmt=None):
	parse = urlparse(website)
	return parse.netloc.split(':')[0]

#routes
@app.route('/')
def redirect_to_page():
	return redirect('/posts/1/')
@app.route('/posts/<page>/')
def posts(page):

	post = post_model.post()

	# round down to the closest multiple of page_size to get the page total
	# add 1 to compensate for offset
	page_count = int((post.total_count - post.total_count % post.page_size) / post.page_size) + 1
	if(post.total_count % post.page_size):
		page_count += 1

	if(int(page) > page_count):
		return redirect('/posts/' +str( page_count))
	offset = (int(page) - 1) * post.page_size

	try:
		post_list = post.get_posts([], offset)
	except sqlite3.OperationalError as e:
		return render_template('posts.html', posts=[],page_count=0, error="db_locked")
	

	return render_template('posts.html', posts=post_list, page_count=page_count)
@app.route('/crawl')
def crawl():
	c = crawler()
	c.crawl_posts(c.get_sources()[:2])
	return "True"
@app.route('/sources/')
def sources():
	source = source_model.source()
	sources = source.get_all()
	return render_template('sources.html', sources=sources)
@app.route('/import_sources/')
def import_sources():
	source = source_model.source()
	errored_sources = source.import_sources('sources.txt')
	sources = source.get_all()
	return render_template('sources.html',sources=sources, errors=errored_sources)

