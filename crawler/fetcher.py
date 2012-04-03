# -*- coding: utf-8 -*-


import threading
import time
import urllib.parse

from urlhandler import *
from extractor import *

from gephiAPI import GephiAPI
from mongoAPI import MongodbAPI
from opaAPI import OpaAPI

class Fetcher(threading.Thread):
	def __init__(self, robot, queue_in, queue_out, max_depth, *, db_host, db_name, db_async=False, db_location='local'):
		threading.Thread.__init__(self, name="Fetcher-%s"%id(self))
		self.robot = robot
		self.queue_in = queue_in
		self.queue_out = queue_out
		self.max_depth = max_depth
		
		self.urlhandler = UrlHandler(robot=self.robot, max_tries=5)

		self.gephiAPI = []
		for host,port in GEPHI_HOSTS:
			self.gephiAPI.append(GephiAPI(host, port))

		if db_location=='local':
			self.dbAPI = MongodbAPI(db_host, db_name)
		else:
			self.dbAPI = OpaAPI(db_host)

		self.e_stop = threading.Event()

		self._is_working = threading.Event()

		# statistics
		self.nb_opened = 0
		self.nb_saved = 0
		self.stats = {
			'process': [0,0],
			'urlhandler': [0,0],
			'extractor': [0,0],
			'gephi': [0,0],
			'db': [0,0]
		}

		# current url
		self.url = ""

		# shall the db send commands without waiting answer
		self.db_async = db_async

	def stop(self):
		self.e_stop.set()
		self.dbAPI.stop()

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
				time.sleep(2)
				url = params['url']
				depth = params['depth']
				self.exc_and_get_stats(
					name="process",
					target=self._process,
					args=(url,depth)
				)

	def _process(self,url,depth):
		self._is_working.set()
		if self.url_need_a_visit(url):
			html = self.exc_and_get_stats(
					name="urlhandler",
					target=self.get_html,
					args=(url,)
				)
			if html:
				self.nb_opened += 1
				extractor = self.exc_and_get_stats(
					name='extractor',
					target=self.extract,
					args=(html, url)
				)
				if extractor:
					links = extractor.links
					keywords = extractor.keywords
					self.process_result(depth+1, url, links, keywords)
		else:
			print("pas besoin de visiter", url)
		self._is_working.clear()

	def process_result(self, depth, url, links, keywords):
		# gephi
		self.exc_and_get_stats(
			name='gephi',
			target=self.process_result_gephi,
			args=(url, links, keywords)
		)
		# db
		self.exc_and_get_stats(
			name='db',
			target=self.process_result_db,
			args=(url, links, keywords)
		)
		# queue
		if isinstance(self.dbAPI, OpaAPI):
			if self.queue_out.qsize() < 5:
				to_visit = self.dbAPI.get_urls_to_visit(10)
				for link in to_visit:
					result = {'url':link, 'depth':depth}
					self.queue_out.put(result)
		elif depth < self.max_depth:
			for link in links:
				result = {'url':link, 'depth':depth}
				self.queue_out.put(result)

	def process_result_gephi(self, url, links, keywords):
		for api in self.gephiAPI:
			color = {'r':0.0, 'g':1.0, 'b':1.0}
			api.add_node(url, **color)
			api.add_nodes(map(lambda l: (l,color), links))
			api.add_edges(map(lambda l: (url, l, {}), links))

	def process_result_db(self, url, links, keywords):
		lprint("SAVE", url)
		self.nb_saved += 1
		r = self.dbAPI.add_links(url=url, links=links, safe=(not self.db_async))
		#lprint(r)

	def get_html(self, url):
		"""
		Récupérer le contenu d'une page
		"""
		self.url = url		# pour savoir quelle url est entrain d'évaluer le fetcher
		try:
			stream = self.urlhandler.open(url, None)
		except ExceptionUrlForbid as ex:
			lprint("ERROR", ex)
		except ExceptionMaxTries as ex:
			lprint("ERROR", ex)
		except Exception as ex:
			lprint(url, ex, "\n"+get_traceback())
		else:
			lprint("OPENED", url)
			html = ""
			try:
				html = stream.read().decode(errors='replace')
			except Exception as ex:
				lprint(get_traceback(), "\n", url, ex, )
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
			lprint("ERROR", self.__class__.__name__, "extract :", ex, url, "\n"+get_traceback())
		else:
			return extractor
		
	def url_need_a_visit(self, url):
		#return True
		p = urllib.parse.urlparse(url)
		if p.scheme in ('http','https'):
			return self.dbAPI.url_need_a_visit(url)
		else:
			return False			

	def exc_and_get_stats(self, *, name, target, args=(), kwargs={}):
		start = time.time()
		r = target(*args,**kwargs)
		ellapsed = time.time() - start
		self.stats[name][0] += ellapsed
		self.stats[name][1] += 1
		return r
		
	def __line(self, name, val, tab):
		s_tab = "\t"*tab
		return "{:.<40}{}\n".format(s_tab+name,val)
		
	def __repr__(self):
			
		s = "{:*^60}\n".format(self.name)
		s += self.__line("Working", self.is_working(), 0)
		s += self.__line("CurrentUrl", self.url, 0)
		s += self.__line("TotOpened", self.nb_opened, 0)
		s += self.__line("TotSaved", self.nb_saved, 0)
		s += "Stats:\n"
		for k, (t,n) in self.stats.items():
			if n:
				val = "{:.3f}s ({}iters)".format(t/n, n)
				s += self.__line(k, val, 1)
		return s










		
	
