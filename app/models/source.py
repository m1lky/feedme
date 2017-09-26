from .database import database
import sqlite3

class source(database):
	def __init__(self, dbname):
		database.__init__(self, dbname)
		self.columns = ['hash', 'url', 'category']
		self.hash_columns = ['url', 'category']
		self.table_name = "sources"

		try:
			result = self.cursor.execute("select count(hash) from sources").fetchall()
			self.total_count = result[0]['count(hash)']
		except sqlite3.OperationalError as e:
			self.cursor.execute("create table " + self.table_name + " (hash text primary key, url text, category text )")
			self.conn.commit()
			self.total_count = 0
		self.page_size = self.total_count
	
	def import_sources(self, source_file ):
		errored_sources = []
		with open(source_file) as f:
			for line in f.readlines():
				src_arr = line.split(' ')
				src = {'url':src_arr[0], 'category':src_arr[1]}
				duplicate = self.insert(src)
				if( not duplicate):
					errored_sources.append(src_arr[0])
		self.conn.commit()
		return errored_sources
	def get_all(self):
		return self.cursor.execute('select * from sources').fetchall()
		
