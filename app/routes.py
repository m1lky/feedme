from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
@app.route('/reddit')
def reddit_crawler():
	return "reddit"