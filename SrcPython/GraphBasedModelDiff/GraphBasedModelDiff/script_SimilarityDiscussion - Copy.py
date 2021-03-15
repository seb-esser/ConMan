
from neo4j_middleware.neo4jGraphFactory import neo4jGraphFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector

from matplotlib import pyplot as plt

# defs


def generateModel1(connector, timestamp):
	cy = neo4jGraphFactory.CreateRootedNode("NwVbQ3K3YQLO6GsWrQ", "ShapeElement", timestamp)
	rootNodeId = connector.run_cypher_statement(cy, 'ID(n)')[0]
	
	attrDict_rooted = {'p21_id': 4 }
	cy = neo4jGraphFactory.AddAttributesToNode(rootNodeId, attrDict_rooted, timestamp)
	connector.run_cypher_statement(cy)
	
	# build line 1
	cy = neo4jGraphFactory.CreateAttributeNode(rootNodeId, "Line", "Representation",timestamp)
	line1_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_line1 = {'Name': "Line 1",
					  'p21_id': 1}
	cy = neo4jGraphFactory.AddAttributesToNode(line1_node, attrDict_line1, timestamp1)
	connector.run_cypher_statement(cy)
	
	# build points
	# points of line 1
	cy = neo4jGraphFactory.CreateAttributeNode(line1_node, "Point", "StartPoint", timestamp)
	point1_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point1 = {'XCoord': 0,
					  'YCoord': 2.0,
					  'ZCoord': 0,
					  'p21_id': 2}
	cy = neo4jGraphFactory.AddAttributesToNode(point1_node, attrDict_point1, timestamp)
	connector.run_cypher_statement(cy)
	
	cy = neo4jGraphFactory.CreateAttributeNode(line1_node, "Point", "EndPoint", timestamp)
	point2_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point2 = {'XCoord': 1.0,
					  'YCoord': 5.5,
					  'ZCoord': 0,
					  'p21_id': 3}
	cy = neo4jGraphFactory.AddAttributesToNode(point2_node, attrDict_point2, timestamp)
	connector.run_cypher_statement(cy)


# --- script --- 

connector = Neo4jConnector()
connector.connect_driver()

timestamp1 = "simExplModel4"

cy = 'MATCH (n:{}) DETACH DELETE n'.format(timestamp1)
connector.run_cypher_statement(cy)

# generate model 1
generateModel1(connector, timestamp1)


connector.disconnect_driver()


