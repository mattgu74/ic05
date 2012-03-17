# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import urllib.parse
import threading
import queue
import json

from tools import *

class MongodbAPI:
	def __init__(self, host='localhost', port=27080, dbname='mydb'):
		self.host = host
		self.port = port
		self.dbname = dbname

		self.test()
		self.connect()
		
		
		self.queue = queue.Queue()
		self.e_stop = threading.Event()
		
		self.t = threading.Thread(target=self.loop_send, name="MongoAPI.loop_send")
		self.t.setDaemon(True)
		self.t.start()

	def server_url(self):
		return "http://{host}:{port}/".format(
			host=self.host,
			port=self.port
		)

	def test(self):
		url = self.server_url()+"/_hello"
		r = urllib.request.urlopen(url)
		r = eval(r.read().decode())
		if r['ok'] != 1:
			raise Exception("L'api rest mongodb n'est probablement pas lancée, retour=%s" % r)

	def connect(self):
		url = self.server_url()+"/_connect"
		req = {"server": self.server_url()}
		req = json.dumps(req).encode()
		r = urllib.request.urlopen(url, req)
		r = eval(r.read().decode())
		if r['ok'] != 1:
			raise Exception("Connection avec l'api rest mongodb impossible, retour=%s" % r)

	def stop(self):
		self.e_stop.set()
	
	def add_page(self, *, url, links):
		page = {
			'url': url,
			'childs': links
		}
		return self.insert(page)

	def url_need_a_visit(self, url):
		r = self.find({'url':url})
		if 'ok' in r if r['ok'] == 1 and r['results']:
			return len(r['result'][0]['l']) == 0
		else:
			return True

	def get_urls_to_visit(self, max_urls):
		r = self.find('pages', criteria={'links':[]}, limit=max_urls)
		if 'ok' in r if r['ok'] == 1 and r['results']:
			return list(map(lambda x: x['url'], r['result']))
		else:
			return []
	
	
	def insert(self, collection,  obj):
		""" low level api """
		if not isinstance(obj,list):
			obj = [obj,]
		return self.send(collection, "_insert", {"docs":json.dumps(obj)})

	def remove(self, collection, criteria=None):
		""" low level api """
		params = {}
		if criteria: params['criteria'] = criteria
		return self.send(collection, "_remove", params)

	def find(self, collection, **kwargs):
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
		options = ('criteria','fields','sort','skip','limit','explain','batch_size')
		params = {}
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
		if get_request:
			for k,v in req.items():
				req[k] = json.dumps(v)
			url += "?"+urllib.parse.urlencode(req)
			encoded_req = None
		else:
			encoded_req = urllib.parse.urlencode(req).encode()
		obj = None
		try:
			r = urllib.request.urlopen(url, encoded_req)
		except urllib.error.URLError as ex:
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
	api = MongodbAPI()
	print("\nremove all")
	print(api.remove('test'))
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
