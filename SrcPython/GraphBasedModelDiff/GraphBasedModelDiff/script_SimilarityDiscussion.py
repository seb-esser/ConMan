
from matplotlib import pyplot as plt

from neo4j_middleware.Neo4jGraphFactory import Neo4jGraphFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector


# defs


def generateModel1(connector, timestamp):
	cy = Neo4jGraphFactory.create_primary_node("guid987654321", "Shapeelement", timestamp)
	rootNodeId = connector.run_cypher_statement(cy, 'ID(n)')[0]
	
	attrDict_rooted = {'p21_id': 10 }
	cy = Neo4jGraphFactory.add_attributes_by_node_id(rootNodeId, attrDict_rooted, timestamp)
	connector.run_cypher_statement(cy)
	
	# build line 1
	cy = Neo4jGraphFactory.create_secondary_node(rootNodeId, "Line", "Representation_item1", timestamp)
	line1_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_line1 = {'Name': "Line 1",
					  'p21_id': 1}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(line1_node, attrDict_line1, timestamp1)
	connector.run_cypher_statement(cy)
	
	# build line 2
	cy = Neo4jGraphFactory.create_secondary_node(rootNodeId, "Line", "Representation_item2", timestamp)
	line2_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_line2 = {'Name': "Line 2",
					  'p21_id': 4}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(line2_node, attrDict_line2, timestamp)
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
	
	# points of Line 2
	cy = Neo4jGraphFactory.create_secondary_node(line2_node, "Point", "StartPoint", timestamp)
	point3_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point3 = {'XCoord': 1.0,
					  'YCoord': 5.5,
					  'ZCoord': 0,
					  'p21_id': 5}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(point3_node, attrDict_point3, timestamp)
	connector.run_cypher_statement(cy)
	
	cy = Neo4jGraphFactory.create_secondary_node(line2_node, "Point", "EndPoint", timestamp)
	point4_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point4 = {'XCoord': 7.0,
					  'YCoord': 3.0,
					  'ZCoord': 0,
					  'p21_id': 6}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(point4_node, attrDict_point4, timestamp)
	connector.run_cypher_statement(cy)
	
def generateModel2(connector, timestamp):
	cy = Neo4jGraphFactory.create_primary_node("guid123456789", "Shapeelement", timestamp)
	rootNodeId = connector.run_cypher_statement(cy, 'ID(n)')[0]
	
	attrDict_rooted = {'p21_id': 10 }
	cy = Neo4jGraphFactory.add_attributes_by_node_id(rootNodeId, attrDict_rooted, timestamp)
	connector.run_cypher_statement(cy)
	
	# build line 1
	cy = Neo4jGraphFactory.create_secondary_node(rootNodeId, "Line", "Representation_item1", timestamp)
	line1_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_line1 = {'Name': "Line 1",
					  'p21_id': 1}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(line1_node, attrDict_line1, timestamp)
	connector.run_cypher_statement(cy)
	
	# build line 2
	cy = Neo4jGraphFactory.create_secondary_node(rootNodeId, "Line", "Representation_item2", timestamp)
	line2_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_line2 = {'Name': "Line 2",
					  'p21_id': 4}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(line2_node, attrDict_line2, timestamp)
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
	
	# points of Line 2
	#cy = Neo4jGraphFactory.CreateAttributeNode(line2_node, "Point", "StartPoint", timestamp)
	#point3_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	#attrDict_point3 = {'XCoord': 1.0,
	#				  'YCoord': 5.5,
	#				  'ZCoord': 0,
	#				  'p21_id': 5}
	#cy = Neo4jGraphFactory.AddAttributesToNode(point3_node, attrDict_point3, timestamp)
	#connector.run_cypher_statement(cy)
	
	# merge point2 to line2->startPoint
	cy = Neo4jGraphFactory.merge_on_node_ids(line2_node, point2_node, "StartPoint")
	connector.run_cypher_statement(cy)


	cy = Neo4jGraphFactory.create_secondary_node(line2_node, "Point", "EndPoint", timestamp)
	point4_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point4 = {'XCoord': 7.0,
					  'YCoord': 3.0,
					  'ZCoord': 0,
					  'p21_id': 6}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(point4_node, attrDict_point4, timestamp)
	connector.run_cypher_statement(cy)
	
def generateModel3(connector, timestamp): 
	cy = Neo4jGraphFactory.create_primary_node("guid456789123", "Shapeelement", timestamp)
	rootNodeId = connector.run_cypher_statement(cy, 'ID(n)')[0]
	
	attrDict_rooted = {'p21_id': 10 }
	cy = Neo4jGraphFactory.add_attributes_by_node_id(rootNodeId, attrDict_rooted, timestamp)
	connector.run_cypher_statement(cy)
	
	# build line 1
	cy = Neo4jGraphFactory.create_secondary_node(rootNodeId, "Polyline 1", "Representation_item1", timestamp)
	polyline_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_polyline = {'Name': "Polyline",
					  'p21_id': 1}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(polyline_node, attrDict_polyline, timestamp)
	connector.run_cypher_statement(cy)

	cy = Neo4jGraphFactory.create_secondary_node(polyline_node, "Point", "Points_item1", timestamp)
	point1_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point1 = {'XCoord': 0,
					  'YCoord': 2.0,
					  'ZCoord': 0,
					  'p21_id': 2}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(point1_node, attrDict_point1, timestamp)
	connector.run_cypher_statement(cy)
	
	cy = Neo4jGraphFactory.create_secondary_node(polyline_node, "Point", "Points_item2", timestamp)
	point2_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point2 = {'XCoord': 1.0,
					  'YCoord': 5.5,
					  'ZCoord': 0,
					  'p21_id': 3}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(point2_node, attrDict_point2, timestamp)
	connector.run_cypher_statement(cy)
		
	cy = Neo4jGraphFactory.create_secondary_node(polyline_node, "Point", "Points_item3", timestamp)
	point3_node = connector.run_cypher_statement(cy, 'ID(n)')[0]
	attrDict_point3 = {'XCoord': 7.0,
					  'YCoord': 3.0,
					  'ZCoord': 0,
					  'p21_id': 4}
	cy = Neo4jGraphFactory.add_attributes_by_node_id(point3_node, attrDict_point3, timestamp)
	connector.run_cypher_statement(cy)

def generateModel4(connector, timestamp):
	cy = Neo4jGraphFactory.create_primary_node("NwVbQ3K3YQLO6GsWrQ", "ShapeElement", timestamp)
	rootNodeId = connector.run_cypher_statement(cy, 'ID(n)')[0]

	attrDict_rooted = {'p21_id': 4}
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
# script

plt.plot([0,1,7], [2, 5.5, 3], 'x-')
plt.grid()
#plt.show()

connector = Neo4jConnector()
connector.connect_driver()

timestamp1 = "simExplModel1"
timestamp2 = "simExplModel2"
timestamp3 = "simExplModel3"
timestamp4 = "simExplModel4"

# delete all
cy = 'MATCH (n:{}) DETACH DELETE n'.format(timestamp1)
connector.run_cypher_statement(cy)
cy = 'MATCH (n:{}) DETACH DELETE n'.format(timestamp2)
connector.run_cypher_statement(cy)
cy = 'MATCH (n:{}) DETACH DELETE n'.format(timestamp3)
connector.run_cypher_statement(cy)

# generate model 1
generateModel1(connector, timestamp1)
generateModel2(connector, timestamp2)
generateModel3(connector, timestamp3)
generateModel4(connector, timestamp4)

connector.disconnect_driver()


