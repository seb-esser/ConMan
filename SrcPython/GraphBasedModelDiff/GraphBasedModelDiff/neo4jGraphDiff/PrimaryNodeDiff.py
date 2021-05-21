from neo4jGraphAnalysis.AdjacencyAnalyser import AdjacencyAnalyser
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem

from .SetCalculator import SetCalculator


class RootedNodeDiff:
	""" """
	def __init__(self, connector, configuration): 
		self.configuration = configuration
		self.utils = SetCalculator()
		self.connector = connector
		pass

	def toConsole(self):
		if self.configuration.LogSettings.logToConsole:
			return True
		else:
			return False

	def diffRootedNodes(self, label_init, label_updated):
		""" """
		
		# retrieve nodes
		nodes_init = self.__get_primary_nodes(label_init)
		nodes_updated = self.__get_primary_nodes(label_updated)

		# load attrIgnore list from config
		attr_ignore_list = self.configuration.DiffSettings.diffIgnoreAttrs

		for node in nodes_init: 
			# load hash_value value
			cy = Neo4jQueryFactory.get_hash_by_nodeId(label_init, node.id, attr_ignore_list)
			res = self.connector.run_cypher_statement(cy)
			node.hash_value = res[0][0]

		for node in nodes_updated: 
			cy = Neo4jQueryFactory.get_hash_by_nodeId(label_updated, node.id, attr_ignore_list)
			res = self.connector.run_cypher_statement(cy)
			node.hash_value = res[0][0]

		# calc matching of node sets
		matchingMethod = self.configuration.DiffSettings.MatchingType_RootedNodes

		if self.toConsole():
			print('Matching Method for rooted nodes: {}'.format(matchingMethod))

		[nodes_unchanged, nodes_added, nodes_deleted] = self.utils.calc_intersection(nodes_init, nodes_updated, matchingMethod)

		if self.toConsole(): 
			print('Unchanged rooted nodes: {}'.format(nodes_unchanged))
			print('Added nodes: {}'.format(nodes_added))
			print('Deleted nodes: {}'.format(nodes_deleted))

		# check property updates of unchanged node tuples

		# check adjacencies of unchanged node tuples
		# self.__check_adjacencies(nodes_unchanged)
		# !! not yet sufficient as current nodes in node set dont share direct edges !!

		return [nodes_unchanged, nodes_added, nodes_deleted]

	def __check_adjacencies(self, nodes_unchanged):
		"""
		@param nodes_unchanged:
		@return:
		"""

		# unpack node ids for adjacency matrix
		nodeIds_init: list[int] = []
		nodeIds_updated: list[int] = []

		for pair in nodes_unchanged:
			nodeIds_init.append(pair[0].id)
			nodeIds_updated.append(pair[1].id)

		# calc adjacency matrices
		adjacency_analyser = AdjacencyAnalyser(self.connector)
		adj_mtx_init = adjacency_analyser.get_adjacency_matrix_byNodeIDs(nodeIds_init)
		print(adj_mtx_init)

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
			node.set_hash(res[2])
			nodes.append(node)

		return nodes

	def __get_primary_nodes(self, label):
		cy = Neo4jQueryFactory.get_primary_nodes(label)
		raw = self.connector.run_cypher_statement(cy)

		# unpack neo4j response into a list if NodeItem instances
		res = NodeItem.fromNeo4jResponseWouRel(raw)

		return res

	def __get_con_nodes(self, label):
		cy_conn = Neo4jQueryFactory.get_connection_nodes(label)
		raw_con = self.connector.run_cypher_statement(cy_conn)
		con_nodes = NodeItem.fromNeo4jResponseWouRel(raw_con)
		return con_nodes

	def __get_rooted_con_nodes(self, label):
		primaries = self.__get_primary_nodes(label)
		connections = self.__get_con_nodes(label)

		return primaries + connections
