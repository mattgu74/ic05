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

	def stop(self):
		self.e_stop.set()
	
	def run(self):
		while not self.e_stop.is_set():
			try:
				params = self.queue_in.get(True, 0.5)
			except:
				pass
			else:
				url = params['url']
				depth = params['depth']
				print(("OPEN", url))
				urlhandler = UrlHandler(self.robot, url, 5, self.proxies)
				try:
					urlhandler.open()
				except ExceptionUrlForbid: pass
				except ExceptionMaxTries: pass
				except Exception as ex:
					print(url,ex)
				else:
					html = urlhandler.html
					extractor = Extractor(url, html)
					links = extractor.links
					keywords = extractor.keywords
					result = {
						'url': url,
						'links': links,
						'keywords': keywords,
						'depth': depth
					}
					self.queue_out.put(result)
				
