# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..", "db"))


import threading
import urllib.parse
import time

#from db import *
from gephiAPI import GephiAPI



class Controller(threading.Thread):
	def __init__(self, base_url, queue_in, queue_out, max_depth, db_host, db_port, db_name, collection_name):
		threading.Thread.__init__(self, name="Controller")
		
		self.queue_in = queue_in
		self.queue_out = queue_out
		self.max_depth = max_depth
		
		#self.db = DB(db_host, db_port, db_name, collection_name)
		self.gephiAPI = GephiAPI()
		self.visited = set(base_url)

		self.e_stop = threading.Event()

	def stop(self):
		self.e_stop.set()
	
	def run(self):
		while not self.e_stop.is_set():
			try:
				param = self.queue_in.get(True, 0.5)
			except:
				#print "NOTHING TO CONTROL"
				continue
			else:
				#print "CONTROL", param['url']
				keywords = param['keywords']
				links = [self.normalize_url(param['url'], x) for x in param['links']]
				print("SAVE", param['url'], keywords)
				#self.db.save_page(url, keywords, links)
				self.gephiAPI.add_node(param['url'])
				for link in links:
					self.gephiAPI.add_node(link)
					self.gephiAPI.add_edge(param['url'], link)
				depth = param['depth'] + 1
				if depth < self.max_depth:
					start = time.time()
					for link in links:
						if link not in self.visited:
							result = {'url':link, 'depth':depth}
							self.queue_out.put(result)
							self.visited.add(link)
					print("TIME ADD LINKS %s" % (time.time() - start))
				#print "END CONTROL", param['url']

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
