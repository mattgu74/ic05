# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..", "db"))


import threading
import urllib.parse
import time

#from db import *
from gephiAPI import GephiAPI
from mongodbapi import MongodbAPI
from config import *


class Controller(threading.Thread):
	def __init__(self, queue_in, queue_out, max_depth, db_host, db_port, db_name, collection_name):
		threading.Thread.__init__(self, name="Controller")
		
		self.queue_in = queue_in
		self.queue_out = queue_out
		self.max_depth = max_depth
		
		self.gephiAPI = GephiAPI(GEPHI_HOST, GEPHI_PORT)
		self.mongodbAPI = MongodbAPI(db_host, db_port)

		self.e_stop = threading.Event()
		self._is_working = threading.Event()

	def stop(self):
		self.e_stop.set()

	def is_working(self):
		return self._is_working.is_set()

	def wait_free(self, timeout=None):
		self._is_working.wait(timeout)
	
	def run(self):
		tt = 0
		while not self.e_stop.is_set():
			try:
				param = self.queue_in.get(True, 0.5)
			except:
				#print "NOTHING TO CONTROL"
				continue
			else:
				print("TIME WITHOUT WORKING", time.time() - tt)
				self._is_working.set()
				start = time.time()
				#print "CONTROL", param['url']
				keywords = param['keywords']
				links = [self.normalize_url(param['url'], x) for x in param['links']]
				print("SAVE", param['url'], keywords)
				#self.db.save_page(url, keywords, links)
				self.gephiAPI.add_node(param['url'])
				self.mongodbAPI.add_page(url=param['url'])
				for link in links:
					self.gephiAPI.add_node(link)
					self.gephiAPI.add_edge(param['url'], link)
					self.mongodbAPI.add_link(source=param['url'], target=link)
				depth = param['depth'] + 1
				if depth < self.max_depth:
					start2 = time.time()
					for link in links:
						if self.url_need_a_visit(link):
							result = {'url':link, 'depth':depth}
							self.queue_out.put(result)
					print("TIME ADD LINKS %s" % (time.time() - start2))
				#print "END CONTROL", param['url']
				print("TIME CONTROLLER", time.time() - start)
				self._is_working.clear()
				tt = time.time()

	def url_need_a_visit(self, url):
		return self.mongodbAPI.url_need_a_visit(url)
	
	def normalize_url(self, base_url, url):
		split = urllib.parse.urlsplit(url)
		if not split.hostname:
			url = urllib.parse.urljoin(base_url, split.geturl())
			split = urllib.parse.urlsplit(url)
		if not split.path:
			url += "/"
		return url.lower()
	
	def __repr__(self):
		return "Controller"
