import sqlite3
import binascii as ba
import time
# abstract class, only meant to be inherited
class database:
	conn = None
	cursor = None
	columns = None
	table_name = None
	hash_columns = None
	page_size = None
	total_count = None
	# allows results to be returned as associative arrays, rather than objects
	def dict_factory(self, cursor, row):
		d = {}
		for idx,col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	def __init__(self):
		self.conn = sqlite3.connect('./database/feedme', timeout=10)
		self.conn.execute("PRAGMA journal_mode=WAL")
		self.conn.row_factory = self.dict_factory
		self.cursor = self.conn.cursor()	

	def __del__(self):
		self.conn.commit()
		self.conn.close()
	# compute crc32 hash for checksums
	# @param to_hash	dict|string	given a dictionary, appends hash columns from dict, computes hash
	# @return  string   crc 32 hash of parameter
	def compute_crc32(self, to_hash):
		hash_string = ""
		if(type(to_hash) == dict):
			for c in self.hash_columns:
				if(c in to_hash):
					hash_string += str(to_hash[c])
		else:
			hash_string = to_hash
		return ba.crc32(bytearray(hash_string, 'utf-8'))
	# insert into table if not duplicate based on hash of hash_columns property
	# @return bool successful
	def insert(self, insert_dict):
		duplicate = False
		#need to cast separately, otherwise it casts the function itself to string
		checksum = self.compute_crc32(insert_dict)
		self.cursor.execute("select count(hash) from " + self.table_name +" where hash = ?", [checksum])
		result = self.cursor.fetchall()
		if(result[0]['count(hash)'] > 0):
			return False

		#iterate through all columns to set default values for all columns
		#to prevent having to attribute check everything
		#things that are added regardless of insert dictionary:
		# - hash
		# - timestamp
		col_statement = ""
		values = []
		for col in self.columns:
			col_statement += col + ","
			if(col == "hash"):
				values.append(checksum)
			elif(col == "timestamp"):
				values.append(int(time.time()))
			elif(col in insert_dict):
				values.append(insert_dict[col])
			else:
				values.append(False)
		sanitizing_marks = ("?," * len(values))[:-1]
		try:
			self.cursor.execute('insert into ' + self.table_name + '(' + col_statement[:-1] + ') values(' + sanitizing_marks+')', values)
			self.conn.commit()
		except Exception as e:
			print(e)
			raise
		return True

