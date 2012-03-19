# -*- coding: utf-8 -*-

from urlhandler import UrlHandler
import urllib.parse
import threading
import queue
import json

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

		self.opener = UrlHandler()
		self.opener.addheader('User-agent', 'Galopa')

		self.test()
		self.connect()
		
		
		self.queue = queue.Queue()
		self.e_stop = threading.Event()
		
		self.t = threading.Thread(target=self.loop_send, name="MongoAPI.loop_send")
		self.t.setDaemon(True)
		self.t.start()

	def server_url(self):
		return "http://{host}".format(
			host=self.host,
			port=self.port
		)

	def test(self):
		url = self.server_url()+"/_hello"
		print(url)
		r = self.opener.open(url)
		r = eval(r.read().decode())
		if r['ok'] != 1:
			raise Exception("L'api rest mongodb n'est probablement pas lancée, retour=%s" % r)

	def connect(self):
		url = self.server_url()+"/_connect"
		req = {"server": self.server_url()}
		req = json.dumps(req).encode()
		r = self.opener.open(url, req)
		r = eval(r.read().decode())
		if r['ok'] != 1:
			raise Exception("Connection avec l'api rest mongodb impossible, retour=%s" % r)

	def stop(self):
		self.e_stop.set()
	
	def add_page(self, *, url, links):
		#print("ADD", url, links)
		return self.update('pages', {'_url':url}, {'$set': {'_url':url}, '$pushAll':{'links':links}})

	def url_need_a_visit(self, url):
		r = self.find('pages', {'_url':url})
		if r and 'ok' in r and r['ok'] == 1 and r['results']:
			return len(r['results'][0]['links']) == 0
		else:
			return True

	def get_urls_to_visit(self, max_urls):
		r = self.find('pages', {'links':{'$size':0}}, limit=max_urls)
		if r and 'ok' in r and r['ok'] == 1 and r['results']:
			print(r)
			return list(map(lambda x: x['_url'], r['results']))
		else:
			return []
	
	
	def insert(self, collection,  obj):
		""" low level api """
		if not isinstance(obj,list):
			obj = [obj,]
		return self.send(collection, "_insert", {"docs":obj})

	def update(self, collection, criteria, newobj, upsert=True, multi=False, safe=True):
		"""
		low level
		
		Required arguments:
		criteria=criteria_for_update (object)
		newobj=modifications (object)
		Optional arguments:

		upsert=bool (insert si l'objet n'existe pas)
		multi=bool
		safe=bool
		"""
		params = {
			'criteria': criteria,
			'newobj': newobj,
			'upsert': upsert,
			'multi': multi,
			'safe': safe,
		}
		return self.send(collection, "_update", params)
	
	def remove(self, collection, criteria=None):
		""" low level api """
		params = {}
		if criteria: params['criteria'] = criteria
		return self.send(collection, "_remove", params)

	def find(self, collection, criteria=None, **kwargs):
		"""
		low level api
		
		criteria=search_criteria (object)
		fields=fields_to_return (object)
		sort=sort_fields (object)
		skip=num (number)
		limit=num (number)
		explain=true
		batch_size=num_to_return (number)
		"""
		options = ('fields','sort','skip','limit','explain','batch_size')
		params = {}
		if criteria:
			params['criteria'] = criteria
		for k,v in kwargs.items():
			if k in options:
				params[k] = v
			else:
				raise TypeError("find() got an unexpected keyword argument '%s'" % k)
		return self.send(collection, "_find", params, get_request=True)
	
	def send(self, collection, operation, req, *, get_request=False):
		url = "{server_url}/{dbname}/{collection}/{operation}".format(
			server_url=self.server_url(),
			dbname=self.dbname,
			collection=collection,
			operation=operation
		)
		#print(req)
		for k,v in req.items():
			req[k] = json.dumps(v)
		if get_request:
			url += "?"+urllib.parse.urlencode(req)
			encoded_req = None
		else:
			encoded_req = urllib.parse.urlencode(req).encode()
		obj = None
		try:
			r = self.opener.open(url, encoded_req)
		except Exception as ex:
			print(get_traceback(), "\n", "ERROR", ex, "url=", url, "req=", req)
		else:
			s = r.read().decode()
			r.close()
			obj = json.loads(s)

		return obj

	def loop_send(self):
		while not self.e_stop.is_set():
			try:
				operation, req = self.queue.get(True, 0.5)
			except queue.Empty:
				pass
			else:
				self.send(operation,req)


if __name__ == "__main__":
	api = MongodbAPI(MONGODB_HOST, MONGODB_PORT, 'test_db')
	print("\nremove all")
	print(api.remove('test'))
	print(api.remove('pages'))
	print("\ninsert simple")
	print(api.insert('test',{'x': 42}))
	print("\ninsert double")
	print(api.insert('test',[{'x': 45}, {'x':47}]))
	print("\nremove")
	print(api.remove('test',{'x':45}))
	print("\nfind all")
	print(api.find('test'))
	print("\ninsert list vide")
	print(api.insert('test',{'x':'blabla', 'l':[]}))
	print("\nfind list vide")
	print(api.find('test',criteria={'l':[]}))
	print("update")
	print(api.update('test', {'x': 47}, {'$set':{'a':1}}))
	print("update2")
	print(api.update('test', {'x': 57}, {'$set':{'a':42}}))

	print("add_page")
	print(api.add_page(url="http://bidon.com", links=[]))
	print("add_page")
	print(api.add_page(url="http://hey.com", links=['http://bidon.com']))
	print("find")
	print(api.get_urls_to_visit(40))
