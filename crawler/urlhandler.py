# -*- coding: utf-8 -*-


import urllib.request, urllib.error, urllib.parse
from urllib.request import FancyURLopener
import threading


from config import *
from tools import *

class ExceptionUrlForbid(Exception):
	pass

class ExceptionMaxTries(Exception):
	pass

class UrlHandler(FancyURLopener):
	def __init__(self, robot, proxies):
		FancyURLopener.__init__(self)
		self.addheader('User-agent', 'Galopa')
		
		self.robot = robot
		self.proxies = proxies

		self.max_tries = 1
		
	def open(self, url, data=None, max_tries=None):
		if not max_tries:
			max_tries = self.max_tries
		else:
			self.max_tries = max_tries
		if self.robot.can_fetch(url):
			for _ in range(max_tries):
				try:
					stream = FancyURLopener.open(self, url, data)
				except Exception as ex:
					error = str(ex)+"\n"+get_traceback()
				else:
					return stream
			else:
				raise ExceptionMaxTries("max tries %s : %s" % (url, error))
		else:
			raise ExceptionUrlForbid("robots can't access to %s" % url)
		

