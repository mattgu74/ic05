# -*- coding: utf-8 -*-


import urllib.parse
import urllib.request, urllib.parse, urllib.error

from urllib.robotparser import RobotFileParser

from config import *


__all__ = ["Robot","RobotFileParser"]


class _RobotAllowAll:
	def can_fetch(self, a,b):
		return True
class Robot:
	def __init__(self):
		self.__robots = {}

	def can_fetch(self, url):
		parse = urllib.parse.urlparse(url)
		hostname = parse.hostname
		try:
			robot = self.robot[hostname]
		except Exception:
			roboturl = urllib.parse.urlunparse((parse.scheme,parse.netloc,"robots.txt","","",""))
			robot = RobotFileParser(roboturl)
			try:
				robot.read()
			except Exception:
				robot = _RobotAllowAll()
			self.__robots[hostname] = robot
		return robot.can_fetch("*", url)



if __name__ == "__main__":

	r = RobotFileParser("http://www.letudiant.fr", {})
	r.read()
	print(r.can_fetch("*", "http://www.letudiant.fr/"))
