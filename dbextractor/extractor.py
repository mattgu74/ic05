
from xml.dom.minidom import Document

from mongoAPI import MongodbAPI
from config import *

"""
<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
    <meta lastmodifieddate="2009-03-20">
        <creator>Gexf.net</creator>
        <description>A hello world! file</description>
    </meta>
    <graph mode="static" defaultedgetype="directed">
        <nodes>
            <node id="0" label="Hello" />
            <node id="1" label="Word" />
        </nodes>
        <edges>
            <edge id="0" source="0" target="1" />
        </edges>
    </graph>
</gexf>
"""

class Extractor:
	"""
	récupère ce qu'il y a dans la db et génère un gexf
	"""
	def __init__(self, db_host, db_port, db_name):
		self.mongodbAPI = MongodbAPI(db_host, db_port, db_name)
		doc = Document()
		self.doc = doc
		gexf = doc.createElement("gexf")
		doc.appendChild(gexf)
		
		meta = doc.createElement("meta")
		gexf.appendChild(meta)
		
		graph = doc.createElement("graph")
		graph.setAttribute("mode","static")
		graph.setAttribute("defaultedgetype","directed")
		gexf.appendChild(graph)
		
		nodes = doc.createElement("nodes")
		graph.appendChild(nodes)

		edges = doc.createElement("edges")
		graph.appendChild(edges)
		
		for p in self.mongodbAPI.find_pages():
			#print(p)
			node = self.create_node_from_page(p)
			nodes.appendChild(node)
			for edge in self.create_edges_from_page(p):
				edges.appendChild(edge)

		self.doc = doc

	def create_node_from_page(self, page):
		i = self.url_to_node_id(page["_url"])
		node = self.doc.createElement("node")
		node.setAttribute("id", i)
		node.setAttribute("label", i)
		return node

	def create_edges_from_page(self, page):
		edges = []
		id_source = self.url_to_node_id(page["_url"])
		for link in page["links"]:
			id_target = self.url_to_node_id(link)
			edge = self.doc.createElement("edge")
			edge.setAttribute("id", id_source+"_to_"+id_target)
			edge.setAttribute("source", id_source)
			edge.setAttribute("target", id_target)
			edges.append(edge)
		return edges

	def url_to_node_id(self, url):
		return url

	def to_xml(self):
		return self.doc.toprettyxml(indent="\t")

if __name__ == "__main__":

	import optparse
	
	default = {}
	
	usage = "usage: %prog [options]"
	parser = optparse.OptionParser(usage,version="%prog 0.0")
	
	(options, _args) = parser.parse_args()

	ex = Extractor(MONGODB_HOST, MONGODB_PORT, MONGODB_DBNAME)

	print(ex.to_xml())

	
