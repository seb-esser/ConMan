

""" package """
import itertools

""" modules """
from .DiffIgnore_parser import DiffIgnore


class DiffUtilities:
	""" """ 
	
	def __init__(self, diffIgnorePath = None):

		if diffIgnorePath != None: 
			self.diffIngore = DiffIgnore.from_json(diffIgnorePath)

		
	def GetHashByNodeId(self, label, nodeId, attrIgnoreList = None):
		getModel = 'MATCH(n:{})'.format(label)
		where = 'WHERE ID(n) = {}'.format(nodeId)

		open_sub = 'CALL {WITH n'
		# ToDo: implement DiffIgnore labels here
		# ToDo: implement DiffIgnore attributes here
		removeLabel = 'REMOVE n:{}'.format(label)
		if attrIgnoreList == None:
			calc_fingerprint = 'with apoc.hashing.fingerprint(n) as hash RETURN hash'
		else:
			ignoreString = self.__buildIgnoreString(attrIgnoreList)
			calc_fingerprint = 'with apoc.hashing.fingerprint(n, {}) as hash RETURN hash'.format(ignoreString)

		close_sub = '}'
		add_label_again = 'SET n:{}'.format(label)
		return_results = 'RETURN hash, n.entityType, ID(n)'
		return [getModel, where, open_sub, removeLabel, calc_fingerprint, close_sub, add_label_again, return_results]


	def ConnectNodesWithSameHash(self, NodeIdFrom, NodeIdTo):
		fromNode = 'MATCH (s) WHERE ID(s) = {}'.format(NodeIdFrom)
		toNode = 'MATCH (t) WHERE ID(t) = {}'.format(NodeIdTo)
		merge = 'MERGE (s)-[r:{}]->(t)'.format('IS_EQUAL_TO')
		return [fromNode, toNode, merge]


	def CompareNodesByHash(self, nodes_init, nodes_updated, considerRelType = True):
		# ToDo: react if hashes occure multiple times in the nodes_lists

		nodes_unchanged = []
		nodes_deleted = []
		nodes_added = []

		
		if considerRelType == False:
			# match nodes based on hash and reltype
			A=nodes_init
			B=nodes_updated
			matched_pairs = ((x,y) for x,y in itertools.product(A, B) if x.hash == y.hash)
						
			nodes_added = nodes_updated
			nodes_deleted = nodes_init

			for pair in matched_pairs:
				nodes_added.remove(pair[1])
				nodes_deleted.remove(pair[0])
				nodes_unchanged.append((pair[0].id, pair[1].id ))

			nodes_added = [x.id for x in nodes_added]
			nodes_deleted = [x.id for x in nodes_deleted]
		
		else:
					
			# match nodes based on hash and reltype
			A=nodes_init
			B=nodes_updated
			matched_pairs = ((x,y) for x,y in itertools.product(A, B) if x.hash == y.hash and x.relType == y.relType)
						
			nodes_added = nodes_updated
			nodes_deleted = nodes_init

			for pair in matched_pairs:
				nodes_added.remove(pair[1])
				nodes_deleted.remove(pair[0])
				nodes_unchanged.append((pair[0].id, pair[1].id ))

			nodes_added = [x.id for x in nodes_added]
			nodes_deleted = [x.id for x in nodes_deleted]

		return nodes_unchanged, nodes_added, nodes_deleted

	def __buildIgnoreString(self, attr_ignore_list):
		""" generates the necessary string to exclude a given list of attributes that should not taken into account when calculating the hashsum""" 
		
		# open 
		my_string = '['

		# all attrs
		for attr in attr_ignore_list:
			my_string = my_string + '"{}", '.format(attr)

		# remove last comma
		my_string = my_string[:-2]
		# close
		my_string = my_string + ']'

		return my_string
