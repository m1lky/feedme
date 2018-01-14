import sqlite3
import os, sys
from .database import database
class image(database):
	def __init__(self):
		database.__init__(self)
		self.table_name = 'images'
		self.columns = ['post_hash','source_hash', 'filename', 'timestamp', 'hash']
		self.hash_columns = ['post_hash', 'source_hash', 'filename', 'timestamp']
		try:
			result = self.cursor.execute("select count(hash) from images").fetchall()
			self.total_count = result[0]["count(hash)"]
		except sqlite3.OperationalError as e:
			self.cursor.execute("create table images (post_hash text, source_hash text, filename text, timestamp text, hash text primary_key)")
			self.total_count = 0
	#return all images related to source
	def get_images_by_source(self, source_hash):
		return self.cursor.execute("select filename from images where source_hash = ?", source_hash).fetchall()
	
	def get_images(self, what_to_get="*"):
		where_clause = ""
		# if(parameters):
		# 	where_clause += " where "
		# 	for index,val in parameters:
		# 		where_clause += index + " = " + val
		query = "select " + what_to_get + " from images" + where_clause
		return self.cursor.execute(query).fetchall()

	def delete(self, image_hash):
		image = self.cursor.execute('select * from images where hash = ' + image_hash).fetchall()
		image_path = os.getcwd() + '/app/static/images/' + image[0]['filename']
		os.remove(image_path)
		self.cursor.execute('delete from images where hash = ' + image_hash)
		self.conn.commit()



