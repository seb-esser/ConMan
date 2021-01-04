

""" package """


""" modules """
from .DiffIgnore_parser import DiffIgnore


class DiffUtilities:
	""" """ 
	
	def __init__(self, diffIgnorePath = None):

		if diffIgnorePath != None: 
			self.diffIngore = DiffIgnore.from_json(diffIgnorePath)

		
	def GetHashes(label):
		getModel = 'MATCH(n:rootedNode:{})'.format(label)
		open_sub = 'CALL {WITH n'
		removeLabel = 'REMOVE n:{}'.format(label)
		calc_fingerprint = 'with apoc.hashing.fingerprint(n, {}) as hash RETURN hash'.format('["p21_id"]')
		close_sub = '}'
		add_label_again = 'SET n:{}'.format(label)
		return_results = 'RETURN hash, n.entityType, ID(n)'
		return [getModel, open_sub, removeLabel, calc_fingerprint, close_sub, add_label_again, return_results]

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


	def ConnectNodesWithSameHash(NodeIdFrom, NodeIdTo):
		fromNode = 'MATCH (s) WHERE ID(s) = {}'.format(NodeIdFrom)
		toNode = 'MATCH (t) WHERE ID(t) = {}'.format(NodeIdTo)
		merge = 'MERGE (s)-[r:{}]->(t)'.format('IS_EQUAL_TO')
		return [fromNode, toNode, merge]


	def CompareNodesByHash(self, nodes_init, nodes_updated):

		nodes_unchanged = []
		nodes_deleted = []
		nodes_added = []

		# loop over all initial nodes
		
		for key, val in nodes_init.items():
			# print('\t hash: {}'.format(key))
			if key in nodes_updated.keys():
				# print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_updated[key], key))

				res = ((val, nodes_updated[key]))

				if res not in nodes_unchanged: 
					nodes_unchanged.append( res )
		
				
				# connector.run_cypher_statement(neo4jUtils.BuildMultiStatement(cypher_connect))
			else: 
				# print('\t[RESULT] No match for hashsum {}. Node {} from the initial graph has no matching partner in the updated graph.'.format(key, val))
				nodes_deleted.append(val);

		
		
		# loop over updated nodes
		for key, val in nodes_updated.items():
			
			if key in nodes_init.keys():
				# print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_init[key], key))
				res = ((nodes_init[key], val))

				if res not in nodes_unchanged: 
					nodes_unchanged.append( res )
		
			else: 
				# print('\t[RESULT] No match for hashsum {}. Node {} from the updated graph has no matching partner in the initial graph.'.format(key, val))
				nodes_added.append(val)

		return nodes_unchanged, nodes_added, nodes_deleted
