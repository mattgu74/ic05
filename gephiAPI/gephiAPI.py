

import urllib.request
import urllib.parse
import urllib.error
import json


from tools import *


class GephiAPI:
	def __init__(self, host="localhost", port=8080):
		self.host = host
		self.port = port

	def add_nodes(self, nodes, *, workspace_id=0):
		"""
		@param nodes list((id,**params)
		"""
		json_addnodes = ""
		for i,params in nodes:
			json_addnodes += json.dumps(self.json_addnode(i, **params)) + "\r"
		self.make_request(json_addnodes, workspace_id)

	def add_edges(self, edges, *, workspace_id=0):
		"""
		@param edges list((src,dst,**params))
		"""
		json_addedges = ""
		for src,dst,params in edges:
			json_addedges += json.dumps(self.json_addedge(src,dst, **params)) + "\r"
		self.make_request(json_addedges, workspace_id)

	def add_node(self, id_node, *, workspace_id=0, **params):
		json_node = self.json_node(id_node, **params)
		json_addnode = json.dumps({"an":json_node})
		self.make_request(json_addnode, workspace_id)

	def json_addnode(self, id_node, label=None, **params):
		return {"an": self.json_node(id_node, label, **params)}
	
	def json_node(self, id_node, label=None, **params):
		if not label:
			params['label'] = id_node
		return {id_node: params}

	def add_edge(self, source, target, *, workspace_id=0, **params):
		json_edge = self.json_edge(source, target, **params)
		json_addedge = json.dumps({"ae":json_edge})
		self.make_request(json_addedge, workspace_id)

	def json_addedge(self, source, target, *, directed=True, id_edge=None, **params):
		return {"ae": self.json_edge(source, target, directed=directed, id_edge=id_edge, **params)}
	
	def json_edge(self, source, target, *, directed=True, id_edge=None, **params):
		params['source'] = source
		params['target'] = target
		params['directed'] = directed
		if not id_edge:
			id_edge = source+'_to_'+target
		return {id_edge: params}
	
	def make_request(self, data, workspace_id):
		#lprint(data.encode())
		url = "http://{host}:{port}/workspace{ws_id}?operation=updateGraph".format(
			host=self.host,
			port=self.port,
			ws_id=workspace_id,
		)
		#lprint(url)
		try:
			r = urllib.request.urlopen(url, data=data.encode())
		except urllib.error.URLError:
			pass
		else:
			r.close()


if __name__ == "__main__":
	import doctest
	doctest.testmod()

	import time
	import sys
	host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
	port = sys.argv[2] if len(sys.argv) > 2 else 8080

	api = GephiAPI(host, port)
	api.add_node("Node1")
	api.add_node("Node2")
	api.add_edge("Node1", "Node2")

	time.sleep(1)



	
