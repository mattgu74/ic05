#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import threading
from queue import Queue, LifoQueue


from urlhandler import *
from extractor import *
from fetcher import *
from config import *
from tools import *
from robot import *


class Crawler:
	def __init__(self, n_threads_fetchers, max_depth, db_host, db_port, db_name, *,
			feeds=[],
			nb_ask_feeds=0):
				
		self.queue_fetchers = LifoQueue()
		self.robot = Robot()
		self.fetchers = [
			Fetcher(self.robot, self.queue_fetchers, self.queue_fetchers, max_depth, PROXIES,
				db_host=db_host, db_port=db_port, db_name=db_name
			)
			for _ in range(n_threads_fetchers)
		]

		
		if not feeds and nb_ask_feeds < 1:
			nb_ask_feeds = 1

		if nb_ask_feeds > 0:
			feeds += self.fetchers[0].mongodbAPI.get_urls_to_visit(nb_ask_feeds)

		print(feeds)

		for feed in feeds:
			x = {'url':normalize_url("", feed), 'depth':0}
			self.queue_fetchers.put(x)

		for t in self.fetchers:
			t.start()

		self.e_stop = threading.Event()


	def loop(self):
		n_inactivity = 0
		while not self.e_stop.is_set():
			nb_fetchers_working = 0
			for fetcher in self.fetchers:
				if fetcher.is_working():
					nb_fetchers_working += 1
			if nb_fetchers_working == 0:
				n_inactivity += 1
				if n_inactivity >= 2:
					self.stop()
					break
			print("Nb Fetchers working : %s" % nb_fetchers_working)
			print("Queue Fetchers : %s" % self.queue_fetchers.qsize())
			self.e_stop.wait(5)

	def stop(self):
		print("Closing all fetchers...")
		for fetcher in self.fetchers:
			fetcher.stop()
		print("End")
		self.e_stop.set()
		self.print_result()

	def print_result(self):
		nb_opened = 0
		nb_saved = 0
		for f in self.fetchers:
			print(f)
			print("opened : %s" % f.nb_opened)
			print("saved : %s" % f.nb_saved)
			nb_opened += f.nb_opened
			nb_saved += f.nb_saved
		print("TOTAL OPENED : %s" % nb_opened)
		print("TOTAL SAVED : %s" % nb_saved)
			


if __name__ == "__main__":
	c = Crawler(1, 1, MONGODB_HOST, MONGODB_PORT, MONGODB_DBNAME,
		feeds=["http://www.utc.fr"],
		nb_ask_feeds=2
		)
	try:
		c.loop()
	except KeyboardInterrupt:
		c.stop()
		exit()



			
