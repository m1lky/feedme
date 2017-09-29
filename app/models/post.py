import sqlite3
from .database import database
class post(database):
	def __init__(self):
		database.__init__(self)
		self.table_name = 'posts'
		self.columns = ['title', 'link', 'description', 'timestamp', 'website', 'published', 'image', 'feed_type', 'content', 'hash']
		self.hash_columns = ['title', 'link', 'published']
		self.page_size = 10
		try:
			result = self.cursor.execute("select count(hash) from posts").fetchall()
			self.total_count = result[0]["count(hash)"]
		except sqlite3.OperationalError as e:
			self.cursor.execute("create table posts (title text, link text, description text, timestamp int, website text, published int, image text, feed_type text, content text, hash text primary_key)")
			self.total_count = 0
		
	def delete(self, hash):
		self.cursor.execute("delete from posts where hash = ?", [hash])
		self.conn.commit()

	def get_posts(self, parameters, offset=0):

		where_clause = ""
		if('website' in parameters):
			where_clause += " where website like '%" + parameters['website'] + "%'"
		#todo: add category filter
		
		result = self.cursor.execute('select * from posts'+where_clause+' order by timestamp limit '+str(self.page_size)+" offset "+str(offset)).fetchall()
				
		return result

	

