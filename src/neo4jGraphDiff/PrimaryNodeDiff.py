from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem

from SetCalculator import SetCalculator


class PrimaryNodeDiff:
	"""

	"""
	def __init__(self, connector, configuration):
		"""

		@param connector: Neo4j Connector instance
		@param configuration:
		"""
		self.configuration = configuration
		self.utils = SetCalculator()
		self.connector = connector
		pass

	def toConsole(self):
		"""

		@return:
		"""
		if self.configuration.LogSettings.logToConsole:
			return True
		else:
			return False

	def diff_primary_nodes(self, label_init, label_updated):
		"""
		compares the sets of primary nodes between to given graphs identified by their timestamp labels
		@param label_init: the graph of the initial model
		@param label_updated: the graph of the updated model
		@return: a list of unchanged (as tuple), added, and deleted primaryNodes
		"""
		
		# retrieve nodes
		nodes_init = self.__get_primary_nodes(label_init)
		nodes_updated = self.__get_primary_nodes(label_updated)

		# calc matching of node sets
		matching_method = self.configuration.DiffSettings.MatchingType_RootedNodes

		if self.toConsole():
			print('Matching Method for rooted nodes: {}'.format(matching_method))

		[nodes_unchanged, nodes_added, nodes_deleted] = self.utils.calc_intersection(nodes_init, nodes_updated, matching_method)

		if self.toConsole(): 
			print('Unchanged rooted nodes: {}'.format(nodes_unchanged))
			print('Added nodes: {}'.format(nodes_added))
			print('Deleted nodes: {}'.format(nodes_deleted))

		return [nodes_unchanged, nodes_added, nodes_deleted]

	def __get_primary_nodes(self, label):
		cy = Neo4jQueryFactory.get_primary_nodes(label)
		raw = self.connector.run_cypher_statement(cy)

		# unpack neo4j response into a list if NodeItem instances
		res = NodeItem.from_neo4j_response_wou_rel(raw)

		return res

	def __get_con_nodes(self, label):
		cy_conn = Neo4jQueryFactory.get_connection_nodes(label)
		raw_con = self.connector.run_cypher_statement(cy_conn)
		con_nodes = NodeItem.from_neo4j_response_wou_rel(raw_con)
		return con_nodes

