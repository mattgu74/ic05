

import urllib.request
import urllib.parse
import urllib.error
from tools import *
from config import *
import json

class OpaAPI:
	def __init__(self, host='http://localhost'):
		self.host = host
		self.nodes = set()
		self.edges = set()

	def add_links(self, url, links, **kwargs):
		d = {
			'url': url,
			'links': links
		}
		data = json.dumps(d)
		return self.send("add_liens", data)

	def get_urls_to_visit(self, limit, **kwargs):
		"""
		@todo limit
		"""
		return self.send("get_urls")

	def url_need_a_visit(self, url, **kwargs):
		return self.send("need_a_visit", url)
		
	def send(self, cmd, data=None):
		url = "%s/_rest_/%s" % (self.host, cmd)
		#print(url)
		try:
			if data:
				handler = urllib.request.urlopen(url, data.encode())
			else:
				handler = urllib.request.urlopen(url)
		except urllib.error.URLError as ex:
			r = (get_traceback()+"\n"+str(ex))
		else:
			r = handler.read().decode()
			if r:
				r = json.loads(r)
			else:
				r = True
			handler.close()
		return r

	def stop(self):
		pass

if __name__ == "__main__":
	api = OpaAPI(OPA_HOST)

	print("get_urls")
	print(api.get_urls_to_visit(1))
	#print("add_links")
	#print(api.add_links("http://bidon.com", ["http://hello.com", "http://bonjour.com"]))
	print("need_a_visit")
	print(api.url_need_a_visit("http://www.utc.fr"))
	#print(api.url_need_a_visit("http://hello.com"))



	
