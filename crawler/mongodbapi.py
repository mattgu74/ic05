# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import threading


from tools import *


def dict_to_json(d):
	return str(d).replace("'", '"').replace('""', '"')
	
class MongodbAPI:
	def __init__(self, host='localhost', port=8080):
		self.host = host
		self.port = port

	def add_page(self, *, url):
		page = {
			'url': url
		}
		self.send("add_page", dict_to_json(page), block=False)

	def add_link(self, *, source, target):
		link = {
			'source': source,
			'target': target,
		}
		self.send("add_link", dict_to_json(link), block=False)

	def url_need_a_visit(self, url):
		url = { 'url' : url }
		r = self.send("url_need_a_visit", dict_to_json(url))
		return r == 'true'

	def get_urls_to_visit(self, max_urls):
		req = {'nb_max': max_urls}
		r = self.send("get_urls_to_visit", dict_to_json(req))
		return eval(r)
	
	def send(self, operation, req, *, block=True):
		url = "http://{host}:{port}/_rest_/{operation}".format(
			host=self.host,
			port=self.port,
			operation=operation
		)
		encoded_req = req.encode()
		def _f():
			try:
				r = urllib.request.urlopen(url, encoded_req)
			except urllib.error.URLError as ex:
				print("ERROR", self.__class__.__name__, "send :", ex, "url=", url, "req=", req, "\n"+get_traceback())
			else:
				return r
		if block:
			r = _f()
			return r.read().decode() if r else ""
		else:
			t = threading.Thread(target=_f)
			t.start()




