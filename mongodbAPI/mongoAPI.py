# -*- coding: utf-8 -*-


import pymongo



from tools import *
from config import *

class MongodbAPI:
	"""
	API interfacer avec sleepy mongoose
	"""
	def __init__(self, host='localhost', port=27080, dbname='mydb'):
		
		self.host = host
		self.port = port
		self.dbname = dbname

		self.connection = pymongo.Connection(host, port)
		self.db = self.connection[dbname]

		self.e_stop = threading.Event()

	def remove_all(self):
		try:
			r = self.db['pages'].remove()
		except Exception as ex:
			print(get_traceback(),"\n",ex)
		else:
			return r

	def stop(self):
		self.e_stop.set()
	
	def add_page(self, *, url, links, safe=True):
		#lprint("ADD", url, links)
		try:
			r = self.db['pages'].update({'_url':url}, {'$set': {'_url':url}, '$addToSet':{'links': {"$each": links}}}, safe=safe, upsert=True)
		except pymongo.errors.DuplicateKeyError:
			pass
		except Exception as ex:
			print(get_traceback(),"\n",ex)
		else:
			return r

	def add_empty_pages(self, urls, *, safe=True):
		if urls:
			datas = list(( {'_url':url, 'links':[]} for url in urls ))
			try:
				r = self.db['pages'].insert(datas, continue_on_error=True, safe=safe)
			except pymongo.errors.DuplicateKeyError:
				pass
			except Exception as ex:
				print(get_traceback(),"\n",ex)
			else:
				return r

	def url_need_a_visit(self, url):
		try:
			r = self.db['pages'].find_one({'_url':url})
		except Exception as ex:
			print(get_traceback(),"\n",ex)
		else:
			return (not r) or ('links' not in r) or (not r['links'])

	def get_urls_to_visit(self, max_urls):
		try:
			r = self.db['pages'].find({'links':{'$size':0}}, limit=max_urls)
		except Exception as ex:
			print(get_traceback(),"\n",ex)
		else:
			return list(map(lambda x: x['_url'], r))

	def find_pages(self):
		try:
			r = self.db['pages'].find()
		except Exception as ex:
			print(get_traceback(),"\n",ex)
		return r
		


if __name__ == "__main__":
	import time
	api = MongodbAPI(MONGODB_HOST, MONGODB_PORT, 'test')
	print("remove_all")
	#print(api.remove_all())
	print("need visit ?")
	print(api.url_need_a_visit("http://bidon.com"))
	print("add_page")
	print(api.add_page(url="http://bidon.com", links=[]))
	print("need visit ?")
	print(api.url_need_a_visit("http://bidon.com"))
	print("add_page")
	print(api.add_page(url="http://hey.com", links=['http://bidon.com']))
	print("find")
	print(api.get_urls_to_visit(40))
	print("add empty pages")
	print(api.add_empty_pages(["http://bidon.com", "http://hey.com", "http://coucou.fr", "http://youhou.fr"]))
	print("pages")
	for p in api.find_pages():
		print(p)
	print("remove_all")
	#print(api.remove_all())

	api.stop()

	
