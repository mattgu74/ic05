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
	def __init__(self, n_threads_fetchers, max_depth, db_host, db_port, db_name, collection_name, *,
			feeds=[],
			nb_ask_feeds=0):
				
		self.queue_fetchers = LifoQueue()
		self.queue_controller = Queue()
		self.controller = Controller(self.queue_controller, self.queue_fetchers, max_depth, db_host, db_port, db_name, collection_name)
		self.robot = Robot()
		self.fetchers = [ Fetcher(self.robot, self.queue_fetchers, self.queue_controller, PROXIES) for _ in range(n_threads_fetchers) ]

		
		if not feeds and nb_ask_feeds < 1:
			nb_ask_feeds = 1

		if nb_ask_feeds > 0:
			feeds += self.controller.mongodbAPI.get_urls_to_visit(nb_ask_feeds)

		for feed in feeds:
			x = {'url':self.controller.normalize_url("", feed), 'depth':0}
			self.queue_fetchers.put(x)

		for t in self.fetchers:
			t.setDaemon(True)
			t.start()
		self.controller.start()

		self.e_stop = threading.Event()


	def loop(self):
		while not self.e_stop.is_set():
			nb_fetchers_working = 0
			for fetcher in self.fetchers:
				if fetcher.is_working():
					nb_fetchers_working += 1
			if nb_fetchers_working == 0 and not self.controller.is_working():
				self.stop()
				break
			print("Nb Fetchers working : %s" % nb_fetchers_working)
			print("Controller working : %s" % self.controller.is_working())
			print("Queue Fetchers : %s" % self.queue_fetchers.qsize())
			print("Queue Controller : %s" % self.queue_controller.qsize())
			self.e_stop.wait(5)

	def stop(self):
		print("Closing all fetchers...")
		for fetcher in self.fetchers:
			fetcher.stop()
		print("Closing Controller...")
		self.controller.stop()
		print("End")
		self.e_stop.set()



if __name__ == "__main__":
	c = Crawler(10, 4, MONGODB_HOST, MONGODB_PORT, MONGODB_DBNAME, MONGODB_COLLECTION,
		feeds=[],
		nb_ask_feeds=100)
	try:
		c.loop()
	except KeyboardInterrupt:
		c.stop()
		exit()



			
