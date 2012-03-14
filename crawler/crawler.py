#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import threading
from queue import Queue, LifoQueue


from urlhandler import *
from extractor import *
from fetcher import *
from controller import *
from config import *
from robot import *


class Crawler:
	def __init__(self, base_url, n_threads_fetchers, max_depth, db_host, db_port, db_name, collection_name):
	#def __init__(self, base_url, n_threads_openers, n_threads_extractors, max_depth, db_host, db_port, db_name, collection_name):
		self.queue_fetchers = LifoQueue()
		self.queue_controller = Queue()
		self.robot = Robot()
		self.controller = Controller(base_url, self.queue_controller, self.queue_fetchers, max_depth, db_host, db_port, db_name, collection_name)
		

		self.fetchers = [ Fetcher(self.robot, self.queue_fetchers, self.queue_controller, PROXIES) for _ in range(n_threads_fetchers) ]
		for t in self.fetchers:
			t.setDaemon(True)
			t.start()
		self.controller.start()

		x = {'url':self.controller.normalize_url("", base_url), 'depth':0}
		self.queue_fetchers.put(x)

		self.e_stop = threading.Event()


	def loop(self):
		while not self.e_stop.is_set():
			#print self.queue_urlhandlers.qsize()
			print("Queue Fetchers : %s" % self.queue_fetchers.qsize())
			print("Queue Controller : %s" % self.queue_controller.qsize())
			self.e_stop.wait(5)

	def stop(self):
		print("Closing all fetchers...")
		for fetcher in self.fetchers:
			fetcher.stop()
		print("Closin Controller...")
		self.controller.stop()
		print("End")
		self.e_stop.set()



if __name__ == "__main__":
	c = Crawler("http://www.utc.fr", 1000, 10, MONGODB_HOST, MONGODB_PORT, MONGODB_DBNAME, MONGODB_COLLECTION)
	try:
		c.loop()
	except KeyboardInterrupt:
		c.stop()
		exit()



			
