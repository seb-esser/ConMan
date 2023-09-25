import jsonpickle
import networkx

from neo4j_middleware.neo4jConnector import Neo4jConnector
from IfcGraphInterface.neo2nxTranslator import Neo2NxConnector

timestamp = "ts20221002T111302"

connector = Neo4jConnector()
connector.connect_driver()

parser = Neo2NxConnector(connector=connector)
nx_graph = parser.translate_neo2nx(timestamp=timestamp)

# write graph to graphml
networkx.write_graphml(G=nx_graph, path="full_ifc_graph_from_neo4j.graphml")

# serialize to jsonpickle

f = open('NetworkX-Graph_{}.json'.format(timestamp), 'w')
f.write(jsonpickle.dumps(nx_graph))
f.close()

