

from .neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

class neo4jQueryFactory: 

	def __init__(self): 
		pass

	@classmethod
	def DiffNodes(cls, nodeIDleft, nodeIDright):
		""" returns a cypher statement to to diff two nodes specified by their node IDs """ 
		
		query_left = 'MATCH (l) WHERE ID(l) = {}'.format(nodeIDleft)
		query_right = 'MATCH (r) WHERE ID(r) = {}'.format(nodeIDright)
		ret_statement = 'RETURN apoc.diff.nodes(l,r)'
		return neo4jUtils.BuildMultiStatement([query_left, query_right, ret_statement])



	@classmethod
	def GetNodeIdByP21(cls, p21_id, label=None):
		""" returns a cypher statement to query a node by its P21_id and a given (optional) label. """ 
		
		query = ''
		if label != None: 
			query = 'MATCH (n:{})'.format(label)
		else: 
			query = 'MATCH (n)'

		wh = 'WHERE n.p21_id = {}'.format(p21_id)
		ret_statement = 'RETURN ID(n)'
		return neo4jUtils.BuildMultiStatement([query, wh, ret_statement])

	
	@classmethod
	def GetRootedNodes(cls, label):
		""" returns a cypher statement to query all rooted nodes with a given label. """ 
		match = 'MATCH (n:rootedNode:{}) '.format(label)
		ret_statement =  'RETURN ID(n), n.entityType'
		return neo4jUtils.BuildMultiStatement([match, ret_statement])

	@classmethod
	def GetHashByNodeId(cls, label, nodeId, attrIgnoreList = None):
		getModel = 'MATCH(n:{})'.format(label)
		where = 'WHERE ID(n) = {}'.format(nodeId)

		open_sub = 'CALL {WITH n'

		removeLabel = 'REMOVE n:{}'.format(label)

		# apply diffIgnore attributes if staged
		if attrIgnoreList == None:
			calc_fingerprint = 'with apoc.hashing.fingerprint(n) as hash RETURN hash'
		else:

			# open 
			ignore_str = '['

			# all attrs
			for attr in attrIgnoreList:
				ignore_str = ignore_str + '"{}", '.format(attr)

			# remove last comma
			ignore_str = ignore_str[:-2]
			# close
			ignore_str = ignore_str + ']'
			
			calc_fingerprint = 'with apoc.hashing.fingerprint(n, {}) as hash RETURN hash'.format(ignore_str)

		close_sub = '}'
		add_label_again = 'SET n:{}'.format(label)
		return_results = 'RETURN hash, n.entityType, ID(n)'
		return neo4jUtils.BuildMultiStatement([getModel, where, open_sub, removeLabel, calc_fingerprint, close_sub, add_label_again, return_results])
		
	@classmethod
	def GetChildNodesByParentNodeId(cls, label, parentNodeId): 

		match = 'MATCH (n:{}) -[r]->(c)'.format(label)
		where = 'WHERE ID(n) = {}'.format(parentNodeId)
		ret = 'RETURN ID(c), type(r), c.entityType'
		return neo4jUtils.BuildMultiStatement([match, where, ret])

	@classmethod
	def GetNodeDataById(cls, nodeId): 
		match = 'MATCH (n)'
		where = 'WHERE ID(n) = {}'.format(nodeId)
		ret = 'RETURN ID(n), n.entityType'
		return neo4jUtils.BuildMultiStatement([match, where, ret])

	@classmethod
	def GetNodePropertiesById(cls, nodeId): 
		match = 'MATCH (n)'
		where = 'WHERE ID(n) = {}'.format(nodeId)
		ret = 'RETURN properties(n)'
		return neo4jUtils.BuildMultiStatement([match, where, ret])

	# ticket_PostEvent-VerifyParsedModel
	# -- create a new method GetNumberOfNodesInGraph(cls, label) here --

