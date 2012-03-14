

import urllib.request
import urllib.parse

class GephiAPI:
	def __init__(self, host="localhost", port=8080):
		self.host = host
		self.port = port

	def add_node(self, id_node, *, label=None, **params):
		if not label:
			params['label'] = id_node
		json_node = self.json_node(id_node, **params)
		json_addnode = str({"an":json_node})
		self.make_request(json_addnode)
	
	def json_node(self, id_node, **params):
		return {id_node: params}

	def add_edge(self, id_edge, *, source, target, directed=True, **params):
		json_edge = self.json_edge(id_edge, source=source, target=target, **params)
		json_addedge = str({"ae":json_edge})
		self.make_request(json_addedge)

	def json_edge(self, id_edge, *, source, target, directed=True, **params):
		params['source'] = source
		params['target'] = target
		params['directed'] = directed
		return {id_edge: params}
	
	def make_request(self, data, workspace_id=0):
		url = "http://{host}:{port}/workspace{ws_id}?operation=updateGraph".format(
			host=self.host,
			port=self.port,
			ws_id=workspace_id,
		)
		print(url)
		urllib.request.urlopen(url, data=data.encode())


if __name__ == "__main__":
	import doctest
	doctest.testmod()

	api = GephiAPI("localhost", 8081)
	api.add_node("Node1")
	api.add_node("Node2")
	api.add_edge("MyEdge", source="Node1", target="Node2")




	
