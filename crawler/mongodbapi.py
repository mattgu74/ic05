# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import threading
import queue

from tools import *


def dict_to_json(d):
	return str(d).replace("'", '"').replace('""', '"')
	
class MongodbAPI:
	def __init__(self, host='localhost', port=8080):
		self.host = host
		self.port = port
		
		self.queue = queue.Queue()
		self.e_stop = threading.Event()
		
		self.t = threading.Thread(target=self.loop_send, name="MongoAPI.loop_send")
		self.t.setDaemon(True)
		self.t.start()


	def stop(self):
		self.e_stop.set()
	
	def add_page(self, *, url):
		page = {
			'url': url
		}
		self.queue.put(("add_page", dict_to_json(page)))

	def add_link(self, *, source, target):
		link = {
			'source': source,
			'target': target,
		}
		self.queue.put(("add_link", dict_to_json(link)))

	def url_need_a_visit(self, url):
		url = { 'url' : url }
		r = self.send("url_need_a_visit", dict_to_json(url))
		return r == 'true'

	def get_urls_to_visit(self, max_urls):
		req = {'nb_max': max_urls}
		r = self.send("get_urls_to_visit", dict_to_json(req))
		return eval(r)
	
	def send(self, operation, req):
		url = "http://{host}:{port}/_rest_/{operation}".format(
			host=self.host,
			port=self.port,
			operation=operation
		)
		encoded_req = req.encode()
		s = ""
		try:
			r = urllib.request.urlopen(url, encoded_req)
		except urllib.error.URLError as ex:
			print("ERROR", self.__class__.__name__, "send :", ex, "url=", url, "req=", req, "\n"+get_traceback())
		else:
			s = r.read().decode()
			r.close()
		finally:
			return s

	def loop_send(self):
		while not self.e_stop.is_set():
			try:
				operation, req = self.queue.get(True, 0.5)
			except queue.Empty:
				pass
			else:
				self.send(operation,req)


