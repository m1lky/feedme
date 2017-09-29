import sqlite3
from .database import database
class log(database):
	def __init__(self):
		database.__init__(self)
		self.table_name = 'logs'
		self.columns = ['event', 'description', 'timestamp', 'hash']
		self.hash_columns = ['event', 'description', 'timestamp']
		self.page_size = 25
		try:
			result = self.cursor.execute("select count(hash) from logs").fetchall()
			self.total_count = result[0]["count(hash)"]
		except sqlite3.OperationalError as e:
			self.cursor.execute("create table logs (event text, description text, timestamp int, hash text)")
			self.total_count = 0
		
	def delete(self, hash):
		self.cursor.execute("delete from log where hash = ?", [hash])
		self.conn.commit()

	def get_log_data(self, parameters, offset=0):
		result = self.cursor.execute('select * from log order by timestamp limit '+str(self.page_size)+" offset "+str(offset)).fetchall()
		return result

	

