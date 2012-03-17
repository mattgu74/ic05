# -*- coding: utf-8 -*-


import threading

from urlhandler import *
from extractor import *

from gephiAPI import GephiAPI
from mongoAPI import MongodbAPI

class Fetcher(threading.Thread):
	def __init__(self, robot, queue_in, queue_out, max_depth, proxies, *, db_host, db_port, db_name):
		threading.Thread.__init__(self, name="Fetcher-%s"%id(self))
		self.robot = robot
		self.queue_in = queue_in
		self.queue_out = queue_out
		self.max_depth = max_depth
		self.proxies = proxies
		
		self.gephiAPI = GephiAPI(GEPHI_HOST, GEPHI_PORT)
		self.mongodbAPI = MongodbAPI(db_host, db_port, db_name)

		self.e_stop = threading.Event()

		self._is_working = threading.Event()

		self.nb_opened = 0
		self.nb_saved = 0

	def stop(self):
		self.mongodbAPI.stop()
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
				if self.url_need_a_visit(url):
					depth = params['depth']
					html = self.get_html(url)
					if html:
						self.nb_opened += 1
						extractor = self.extract(html, url)
						if extractor:
							links = extractor.links
							keywords = extractor.keywords
							self.process_result(depth+1, url, links, keywords)
				self._is_working.clear()

	def process_result(self, depth, url, links, keywords):
		#print("process gephi")
		self.process_result_gephi(url, links, keywords)
		#print("process db")
		self.process_result_db(url, links, keywords)
		#print("add links to queue")
		if depth < self.max_depth:
			for link in links:
				result = {'url':link, 'depth':depth}
				self.queue_out.put(result)

	def process_result_gephi(self, url, links, keywords):
		self.gephiAPI.add_node(url)
		for link in links:
			self.gephiAPI.add_node(link)
			self.gephiAPI.add_edge(url, link)

	def process_result_db(self, url, links, keywords):
		print("SAVE", url)
		self.nb_saved += 1
		r = self.mongodbAPI.add_page(url=url, links=links)
		print(r)
		for link in links:
			r = self.mongodbAPI.add_page(url=link, links=[])
	
	def get_html(self, url):
		"""
		Récupérer le contenu d'une page
		"""
		urlhandler = UrlHandler(self.robot, self.proxies)
		try:
			stream = urlhandler.open(url, None, 5)
		except ExceptionUrlForbid as ex:
			print("ERROR", ex, "\n"+get_traceback())
		except ExceptionMaxTries as ex:
			print("ERROR", ex, "\n"+get_traceback())
		except Exception as ex:
			print(url, ex, "\n"+get_traceback())
		else:
			print("OPENED", url)
			html = ""
			try:
				html = stream.read().decode()
			except Exception as ex:
				print(url, ex, "\n"+get_traceback())
			else:
				stream.close()
			return html

	def extract(self, html, url):
		"""
		Extraires les choses importantes d'une page (liens, mots clefs, ...)
		"""
		try:
			extractor = Extractor(url, html)
		except Exception as ex:
			print("ERROR", self.__class__.__name__, "extract :", ex, url, "\n"+get_traceback())
		else:
			return extractor
		
	def url_need_a_visit(self, url):
		#return True
		p = urllib.parse.urlparse(url)
		if p.scheme in ('http','https'):
			return self.mongodbAPI.url_need_a_visit(url)
		else:
			return False			
