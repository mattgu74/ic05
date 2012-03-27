# -*- coding: utf-8 -*-


import urllib.request, urllib.error, urllib.parse
from urllib.request import FancyURLopener
import threading

from robot import *
from config import *
from tools import *

class ExceptionUrlForbid(Exception):
	pass

class ExceptionMaxTries(Exception):
	pass

class UrlHandler(FancyURLopener):
	def __init__(self, *, robot=None, max_tries=2):
		"""
		@param robot le robot à utiliser, par default pas de robot utilisé, toutes les urls sont visitées
		@param max_tries le nombre maximum d'essais  d'ouverture de l'url
		"""
		FancyURLopener.__init__(self)
		self.addheader('User-agent', 'Galopa')
		
		self.robot = robot

		self.max_tries = max_tries
		
	def open(self, url, data=None, max_tries=None):
		"""
		Ouvrir une url
		@param url
		@param data les data (POST)
		@param max_tries le nombre maximum d'essais, si non préciser la valeur donnée lors de l'initialisation sera prise
		@return un stream
		@throw ExceptionMaxTries quand le nombre maximum de tentatives est atteind
		@throw ExceptionUrlForbid quand le robot n'a pas le droit de visiter l'url
		"""
		if not max_tries:
			max_tries = self.max_tries
		else:
			self.max_tries = max_tries
		if not self.robot or self.robot.can_fetch(url):
			for _ in range(max_tries):
				try:
					stream = FancyURLopener.open(self, url, data)
				except Exception as ex:
					error = get_traceback()+"\n"+str(ex)
				else:
					return stream
			else:
				raise ExceptionMaxTries("max tries %s : %s" % (url, error))
		else:
			raise ExceptionUrlForbid("robots can't access to %s" % url)
		

