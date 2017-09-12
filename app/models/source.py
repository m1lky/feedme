from database import database
import sqlite3

class source(database):
	def __init__(self):
		database.__init__(self, 'feedme')
		try:
			self.cursor.execute("select id from sources limit 1")
		except sqlite3.OperationalError as e:
			self.cursor.execute("create table sources (id integer primary key, url text, category text )")
	def __insert_source(self, src_str):
		src_arr = src_str.split(' ')
		src = [src_arr[0], src_arr[1]]
		self.cursor.execute("insert into sources(url, category) values(?, ?)", src)

	def import_sources(self, source_file ):
		with open(source_file) as f:
			for line in f.readlines():
				self.__insert_source(line)
		self.conn.commit()
	def get_all(self):
		return self.cursor.execute('select * from sources').fetchall()
		
