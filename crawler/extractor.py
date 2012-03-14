# -*- coding: utf-8 -*-
import AlchemyAPI

import xml.dom.minidom
import re
import threading
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from unac import unac_string

class Extractor:
	def __init__(self, url, html):
		self.url = url
		self.html = html

		# BeautifulSoup : links extraction
		self.soup = BeautifulSoup(html)

		# Alchemy : keyword extraction
		self.alchemy = AlchemyAPI.AlchemyAPI()
		self.alchemy.loadAPIKey("api_key.txt")


		# links extraction
		self.links = self.get_links()

		# keywords extraction
		self.keywords = self.get_keywords()
		

	def get_links(self):
		return [ link.get('href') for link in self.soup.find_all('a') if link.get('href') ]


	def get_keywords(self):
		return []
		"""
		params = AlchemyAPI.AlchemyAPI_KeywordParams()
		params.setMaxRetrieve(20)
		params.setKeywordExtractMode('strict')
		params.setOutputMode("json")
		result = self.alchemy.URLGetRankedKeywords(self.url, params)
		s = result.decode()
		json = eval(s)
		keywords = []
		for kw in json['keywords']:
			keywords += kw['text'].split()
		return keywords
		"""
		

