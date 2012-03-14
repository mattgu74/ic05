# -*- coding: utf-8 -*-


import urllib.request, urllib.error, urllib.parse
import threading


from config import *

class ExceptionUrlForbid(Exception):
	pass

class ExceptionMaxTries(Exception):
	pass

class UrlHandler:
	def __init__(self, robot, url, max_tries, proxies):
		self.robot = robot
		self.url = url
		self.max_tries = max_tries
		self.proxies = proxies
		
		self.html = ""

	def open(self):
		if self.robot.can_fetch(self.url):
			for _ in range(self.max_tries):
				try:
					stream = urllib.request.urlopen(self.__make_request())
				except Exception as ex:
					error = str(ex)
				else:
					self.html = stream.read()
					break
			else:
				raise ExceptionMaxTries("fail open %s : %s" % (self.url, error))
		else:
			raise ExceptionUrlForbid("robots can't access to %s" % self.url)
		
	def __make_request(self):
		req = urllib.request.Request(self.url)
		req.add_header('User-agent', 'Galopa')
		return req

