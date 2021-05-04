
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.NodeItem import NodeItem

from .SetCalculator import SetCalculator


class RootedNodeDiff:
	""" """
	def __init__(self, connector, configuration): 
		self.configuration = configuration
		self.utils = SetCalculator()
		self.connector = connector
		pass

	def toConsole(self):
		if self.configuration.LogSettings.logToConsole == True:
			return True
		else:
			return False
		

	def diffRootedNodes(self, label_init, label_updated):
		""" """
		
		# retrieve nodes
		nodes_init = self.__getRootedNodes(label_init)
		nodes_updated = self.__getRootedNodes(label_updated)

		# load attrIgnore list from config
		attr_ignore_list = self.configuration.DiffSettings.diffIgnoreAttrs

		for node in nodes_init: 
			# load hash value
			cy = Neo4jQueryFactory.get_hash_by_nodeId(label_init, node.id, attr_ignore_list)
			res = self.connector.run_cypher_statement(cy)
			node.hash = res[0][0]

			# load attributes
			cy = Neo4jQueryFactory.get_node_properties_by_id(node.id)
			res = self.connector.run_cypher_statement(cy)
			node.setNodeAttributes(res[0][0])

		for node in nodes_updated: 
			cy = Neo4jQueryFactory.get_hash_by_nodeId(label_updated, node.id, attr_ignore_list)
			res = self.connector.run_cypher_statement(cy)
			node.hash = res[0][0]

			# load attributes
			cy = Neo4jQueryFactory.get_node_properties_by_id(node.id)
			res = self.connector.run_cypher_statement(cy)
			node.setNodeAttributes(res[0][0])

		# calc matching of node sets
		matchingMethod = self.configuration.DiffSettings.MatchingType_RootedNodes

		if self.toConsole():
			print('Matching Method for rooted nodes: {}'.format(matchingMethod))

		[nodes_unchanged, nodes_added, nodes_deleted] = self.utils.calc_intersection(nodes_init, nodes_updated,
                                                                                     matchingMethod)

		if self.toConsole(): 
			print('Unchanged rooted nodes: {}'.format(nodes_unchanged))
			print('Added nodes: {}'.format(nodes_added))
			print('Deleted nodes: {}'.format(nodes_deleted))

		return [nodes_unchanged, nodes_added, nodes_deleted]

	def compareRootedNodeRelationships(self):
		""" """
		raise Exception('method compareRootedNodeRelationships is not implemented yet')		


	def __getHashesOfRootedNodes(self, label):
		cy = Neo4jQueryFactory.GetHashesByLabel(label)
		raw = self.connector.run_cypher_statement(cy)
		return self.__extractHashes(raw)
		

	def __extractHashes(self, result): 
		nodes = []
		for res in result: 
			node = NodeItem(res[0], None, res[1])
			node.setHash(res[2])
			nodes.append(node)
	
		return nodes

	def __getRootedNodes(self, label): 
		cy = Neo4jQueryFactory.get_primary_nodes(label)
		raw = self.connector.run_cypher_statement(cy)

		# unpack neo4j response into a list if NodeItem instances
		res = NodeItem.fromNeo4jResponseWouRel(raw)

		return res

