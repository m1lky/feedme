from models import post as post_model
from models import source as source_model
from models import image as image_model
from models import log as log_model
class deleter:
	classes_responsible_for = ['post', 'source', 'image']
	post = None
	source = None
	image = None
	def __init__(self):
		self.post = post_model.post()
		self.source = source_model.source()
		self.image = image_model.image()

	# deletes all posts that have no source, and deletes all images that have no post
	def prune(self):
		posts = self.post.get_posts([],0,'source_hash, hash')
		sources = self.source.get_all('hash')
		post_hashes = []
		sources = [s for ]
		for p in posts:
			if(p['source_hash'] not in sources):
				self.post.delete(p['hash'])
			else:
				post_hashes.append(p['hash'])
		print(post_hashes)
		images = self.image.get_images('hash, post_hash')
		for i in images:
			if(i['post_hash'] not in post_hashes):
				print(i)
				# self.image.delete(i['hash'])
	# deletes a post, source, or image by hash
	def delete(self, what_to_delete, which_one):
		if(what_to_delete in self.classes_responsible_for):
			dbclass = getattr(self, what_to_delete)
		dbclass.delete(which_one)


