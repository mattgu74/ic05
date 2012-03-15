# -*- coding: utf-8 -*-

import urllib.request
import urllib.error

def dict_to_json(d):
	return str(d).replace("'", '"')
	
class MongodbAPI:
	def __init__(self, host='localhost', port=8080):
		self.host = host
		self.port = port

	def add_page(self, *, url):
		page = {
			'url': url
		}
		self.send("add_page", dict_to_json(page))

	def add_link(self, *, source, target):
		link = {
			'source': source,
			'target': target,
		}
		self.send("add_link", dict_to_json(link))

	def url_need_a_visit(self, url):
		url = { 'url' : url }
		r = self.send("url_need_a_visit", dict_to_json(url))
		return r == 'true'
	
	def send(self, operation, req):
		url = "http://{host}:{port}/_rest_/{operation}".format(
			host=self.host,
			port=self.port,
			operation=operation
		)
		encoded_req = req.encode()
		try:
			r = urllib.request.urlopen(url, encoded_req)
		except urllib.error.URLError as ex:
			print(ex)
		else:
			return r.read().decode()




