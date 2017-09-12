import sqlite3

class database:
	conn = None
	cursor = None
	def dict_factory(self, cursor, row):
		d = {}
		for idx,col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	def __init__(self, dbname):
		self.conn = sqlite3.connect(dbname)
		self.conn.row_factory = self.dict_factory
		self.cursor = self.conn.cursor()		
	def __del__(self):
		self.conn.commit()
		self.conn.close()

