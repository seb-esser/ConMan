

""" package """


""" modules """
from .DiffIgnore_parser import DiffIgnore


class DiffUtilities:
	""" """ 
	
	def __init__(self, diffIgnorePath = None):

		if diffIgnorePath != None: 
			self.diffIngore = DiffIgnore.from_json(diffIgnorePath)

		
	def GetHashByNodeId(self, label, nodeId):
		getModel = 'MATCH(n:{})'.format(label)
		where = 'WHERE ID(n) = {}'.format(nodeId)

		open_sub = 'CALL {WITH n'
		# ToDo: implement DiffIgnore labels here
		# ToDo: implement DiffIgnore attributes here
		removeLabel = 'REMOVE n:{}'.format(label)
		# calc_fingerprint = 'with apoc.hashing.fingerprint(n) as hash RETURN hash'

		fingerprint_with_ign = 'with apoc.hashing.fingerprint(n, {}) as hash RETURN hash'.format('["p21_id"]')

		close_sub = '}'
		add_label_again = 'SET n:{}'.format(label)
		return_results = 'RETURN hash, n.entityType, ID(n)'
		return [getModel, where, open_sub, removeLabel, fingerprint_with_ign, close_sub, add_label_again, return_results]


	def ConnectNodesWithSameHash(self, NodeIdFrom, NodeIdTo):
		fromNode = 'MATCH (s) WHERE ID(s) = {}'.format(NodeIdFrom)
		toNode = 'MATCH (t) WHERE ID(t) = {}'.format(NodeIdTo)
		merge = 'MERGE (s)-[r:{}]->(t)'.format('IS_EQUAL_TO')
		return [fromNode, toNode, merge]


	def CompareNodesByHash(self, nodes_init, nodes_updated):

		nodes_unchanged = []
		nodes_deleted = []
		nodes_added = []

		# loop over all initial nodes
		
		all_hashes_init = [n.hash for n in nodes_init]
		all_hashes_updated = [n.hash for n in nodes_updated]

		for node in nodes_init:
			# print('\t hash: {}'.format(key))
			if node.hash in all_hashes_updated:
				# print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_updated[key], key))

				index = all_hashes_updated.index(node.hash)
				res = ((node.id, nodes_updated[index].id))

				if res not in nodes_unchanged: 
					nodes_unchanged.append( res )
		
				
				# connector.run_cypher_statement(neo4jUtils.BuildMultiStatement(cypher_connect))
			else: 
				# print('\t[RESULT] No match for hashsum {}. Node {} from the initial graph has no matching partner in the updated graph.'.format(key, val))
				nodes_deleted.append(node.id);

		
		
		# loop over updated nodes
		for node in nodes_updated:
			
			if node.hash in all_hashes_init:
				# print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_init[key], key))
				
				index = all_hashes_init.index(node.hash)
				res = ((nodes_init[index].id, node.id))

				if res not in nodes_unchanged: 
					nodes_unchanged.append( res )
		
			else: 
				# print('\t[RESULT] No match for hashsum {}. Node {} from the updated graph has no matching partner in the initial graph.'.format(key, val))
				nodes_added.append(node.id)

		return nodes_unchanged, nodes_added, nodes_deleted
