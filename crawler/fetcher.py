# -*- coding: utf-8 -*-


import threading

from urlhandler import *
from extractor import *


class Fetcher(threading.Thread):
	def __init__(self, robot, queue_in, queue_out, proxies):
		threading.Thread.__init__(self, name="Fetcher-%s"%id(self))
		self.robot = robot
		self.queue_in = queue_in
		self.queue_out = queue_out
		self.proxies = proxies

		self.e_stop = threading.Event()

		self._is_working = threading.Event()

	def stop(self):
		self.e_stop.set()

	def is_working(self):
		return self._is_working.is_set()

	def wait_free(self, timeout=None):
		self._is_working.wait(timeout)
	
	def run(self):
		while not self.e_stop.is_set():
			try:
				params = self.queue_in.get(True, 0.5)
			except:
				pass
			else:
				self._is_working.set()
				url = params['url']
				depth = params['depth']
				urlhandler = UrlHandler(self.robot, url, 5, self.proxies)
				try:
					urlhandler.open()
				except ExceptionUrlForbid: pass
				except ExceptionMaxTries: pass
				except Exception as ex:
					print(url,ex)
				else:
					print("OPENED", url)
					html = urlhandler.html
					try:
						extractor = Extractor(url, html)
					except Exception as ex:
						print("ERROR", self.__class__.__name__, ex, url)
					links = extractor.links
					keywords = extractor.keywords
					result = {
						'url': url,
						'links': links,
						'keywords': keywords,
						'depth': depth
					}
					self.queue_out.put(result)
				self._is_working.clear()
				
