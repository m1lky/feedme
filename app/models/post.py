import time
import sqlite3
from database import database
class post(database):
	def __init__(self):
		database.__init__(self, 'feedme')
		try:
			self.cursor.execute("select link from posts limit 1")
		except sqlite3.OperationalError as e:
			self.cursor.execute("create table posts (title text, link text, description text, timestamp int, website text, hash text)")
	def insert(self, article_title, article_link, article_description, site):
		params = [article_title, article_link, article_description, time.time(), site]
		self.cursor.execute("insert into posts(title, link, description, timestamp, website) values(?, ?, ?, ?, ?)", params)
		self.conn.commit()
	def delete(self, id):
		self.cursor.execute("delete from posts where id = ?", [id])
		self.conn.commit()
	def get_posts(self):
		result = self.cursor.execute('select * from posts order by timestamp').fetchall()
		return result