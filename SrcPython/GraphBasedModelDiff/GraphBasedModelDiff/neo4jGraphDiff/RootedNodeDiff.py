
from .DiffUtilities import DiffUtilities
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jQueryUtils
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory 
from neo4j_middleware.NodeData import NodeData 


class RootedNodeDiff:
	""" """
	def __init__(self, connector, configuration): 
		self.configuration = configuration
		self.utils = DiffUtilities()
		self.connector = connector
		pass

	def toConsole(self):
		if self.configuration.LogSettings.logToConsole == True:
			return True
		else:
			return False
		

	def diffRootedNodes(self, label_init, label_updated, attr_ignore_list):
		""" """
		
		# retrieve nodes
		nodes_init = self.__getRootedNodes(label_init)
		nodes_updated = self.__getRootedNodes(label_updated)

		for node in nodes_init: 
			cy = neo4jQueryFactory.GetHashByNodeId(label_init, node.id, attr_ignore_list) 
			res = self.connector.run_cypher_statement(cy)
			node.hash = res[0][0]

		for node in nodes_updated: 
			cy = neo4jQueryFactory.GetHashByNodeId(label_updated, node.id, attr_ignore_list)
			res = self.connector.run_cypher_statement(cy)
			node.hash = res[0][0]

		# ToDo: consider config match criteria here
		[nodes_unchanged, nodes_added, nodes_deleted] = self.utils.CompareNodesByHash(nodes_init, nodes_updated, considerRelType=False)
		
		if self.toConsole(): 
			print('Unchanged rooted nodes: {}'.format(nodes_unchanged))
			print('Added nodes: {}'.format(nodes_added))
			print('Deleted nodes: {}'.format(nodes_deleted))

		return [nodes_unchanged, nodes_added, nodes_deleted]

	def compareRootedNodeRelationships(self):
		""" """
		raise Exception('method compareRootedNodeRelationships is not implemented yet')		


	def __getHashesOfRootedNodes(self, label):
		cy = neo4jQueryFactory.GetHashesByLabel(label)
		raw = self.connector.run_cypher_statement(cy)
		return self.__extractHashes(raw)
		

	def __extractHashes(self, result): 
		nodes = []
		for res in result: 
			node = NodeData(res[0],None, res[1])
			node.setHash(res[2])
			nodes.append(node)
	
		return nodes

	def __getRootedNodes(self, label): 
		cy = neo4jQueryFactory.GetRootedNodes(label)
		raw = self.connector.run_cypher_statement(cy)

		# unpack neo4j response into a list if NodeData instances
		res = NodeData.fromNeo4jResponseWouRel(raw)

		return res

