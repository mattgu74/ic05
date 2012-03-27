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
			nb_ask_feeds=0,
			reset_db=False):
				
		self.queue_fetchers = Queue()
		self.robot = Robot()
		self.fetchers = [
			Fetcher(self.robot, self.queue_fetchers, self.queue_fetchers, max_depth,
				db_host=db_host, db_port=db_port, db_name=db_name, db_async=False
			)
			for _ in range(n_threads_fetchers)
		]

		if reset_db:
			self.fetchers[0].mongodbAPI.remove_all()

		
		if not feeds and nb_ask_feeds < 1:
			nb_ask_feeds = 1

		if nb_ask_feeds > 0:
			feeds += self.fetchers[0].mongodbAPI.get_urls_to_visit(nb_ask_feeds)

		lprint(feeds)

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
				lprint(fetcher)
			if nb_fetchers_working == 0:
				n_inactivity += 1
				if n_inactivity >= 2:
					self.stop()
					break
			lprint("Nb Fetchers working : %s" % nb_fetchers_working)
			lprint("Queue Fetchers : %s" % self.queue_fetchers.qsize())
			self.e_stop.wait(5)

	def stop(self):
		lprint("Closing all fetchers...")
		for fetcher in self.fetchers:
			fetcher.stop()
		lprint("End")
		self.e_stop.set()
		while 1:
			nb_alived = 0
			for f in self.fetchers:
				if f.is_alive():
					nb_alived += 1
					lprint("still waiting for:\n",f)
					f.join(1)
			if nb_alived == 0:
				break
			lprint("%s fetchers are still alive..." % nb_alived)
		self.print_result()

	def print_result(self):
		nb_opened = 0
		nb_saved = 0
		for f in self.fetchers:
			nb_opened += f.nb_opened
			nb_saved += f.nb_saved
		lprint("TOTAL OPENED : %s" % nb_opened)
		lprint("TOTAL SAVED : %s" % nb_saved)
			


if __name__ == "__main__":
	import optparse
	
	default = {}
	default['url'] = ''
	default['ask_feeds'] = 0
	default['reset_db'] = 0
	default['depth'] = 2
	
	usage = "usage: %prog [options]"
	parser = optparse.OptionParser(usage,version="%prog 0.0")
	parser.add_option("-u", "--url",
						action="store", dest="url", default=default["url"],
						help="la ou les urls séparées par une virgule")
	parser.add_option("-d", "--max-depth",
						action="store", dest="depth", type='int', default=default["depth"],
						help="reccusrion maximale")
	parser.add_option("-a", "--ask-feeds",
						action="store", dest="ask_feeds", type='int', default=default["ask_feeds"],
						help="nombre d'urls à demander à la db")
	parser.add_option("-c", "--clean",
						action="store", dest="reset_db", default=default["reset_db"],
						help="supprimer la db ?")
	
	(options, _args) = parser.parse_args()

	c = Crawler(2, options.depth, MONGODB_HOST, MONGODB_PORT, MONGODB_DBNAME,
		feeds			= options.url.split(','),
		nb_ask_feeds	= options.ask_feeds,
		reset_db		= options.reset_db
		)
	try:
		c.loop()
	except KeyboardInterrupt:
		c.stop()
		exit()



			
