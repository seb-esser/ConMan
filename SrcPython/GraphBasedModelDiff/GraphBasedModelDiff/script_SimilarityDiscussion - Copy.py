
from neo4j_middleware.neo4jGraphFactory import Neo4jGraphFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector

from matplotlib import pyplot as plt

# defs


def generateModel1(connector, timestamp):
	cy = Neo4jGraphFactory.create_primary_node("NwVbQ3K3YQLO6GsWrQ", "ShapeElement", timestamp)
	rootNodeId = connector.run_cypher_statement(cy, 'ID(n)')[0]
	
	attrDict_rooted = {'p21_id': 4 }
	cy = Neo4jGraphFactory.add_attributes_by_node_id(rootNodeId, attrDict_rooted, timestamp)
	connector.run_cypher_statement(cy)
	
	# build line 1
	cy = Neo4jGraphFactory.create_secondary_node(rootNodeId, "Line", "Representation", timestamp)
	line1_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_line1 = {'Name': "Line 1",
					  'p21_id': 1}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(line1_node, attrDict_line1, timestamp1)
	connector.run_cypher_statement(cy)
	
	# build points
	# points of line 1
	cy = Neo4jGraphFactory.create_secondary_node(line1_node, "Point", "StartPoint", timestamp)
	point1_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point1 = {'XCoord': 0,
					  'YCoord': 2.0,
					  'ZCoord': 0,
					  'p21_id': 2}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(point1_node, attrDict_point1, timestamp)
	connector.run_cypher_statement(cy)
	
	cy = Neo4jGraphFactory.create_secondary_node(line1_node, "Point", "EndPoint", timestamp)
	point2_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point2 = {'XCoord': 1.0,
					  'YCoord': 5.5,
					  'ZCoord': 0,
					  'p21_id': 3}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(point2_node, attrDict_point2, timestamp)
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


