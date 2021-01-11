

from .neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

class neo4jQueryFactory: 

	def __init__(self): 
		pass

	@classmethod
	def DiffNodes(cls, nodeIDleft, nodeIDright):
		query_left = 'MATCH (l) WHERE ID(l) = {}'.format(nodeIDleft)
		query_right = 'MATCH (r) WHERE ID(r) = {}'.format(nodeIDright)
		ret_statement = 'RETURN apoc.diff.nodes(l,r)'
		return neo4jUtils.BuildMultiStatement([query_left, query_right, ret_statement])



	@classmethod
	def GetNodeIdByP21(cls, p21_id, timestamp=None):

		query = ''
		if timestamp != None: 
			query = 'MATCH (n:{})'.format(timestamp)
		else: 
			query = 'MATCH (n)'

		wh = 'WHERE n.p21_id = {}'.format(p21_id)
		ret_statement = 'RETURN ID(n)'
		return neo4jUtils.BuildMultiStatement([query, wh, ret_statement])

	@classmethod
	def GetHashesByLabel(cls, label):
		getModel = 'MATCH(n:rootedNode:{})'.format(label)
		open_sub = 'CALL {WITH n'
		removeLabel = 'REMOVE n:{}'.format(label)
		calc_fingerprint = 'with apoc.hashing.fingerprint(n, {}) as hash RETURN hash'.format('["p21_id"]')
		close_sub = '}'
		add_label_again = 'SET n:{}'.format(label)
		return_results = 'RETURN ID(n), n.entityType, hash'
		
		return neo4jUtils.BuildMultiStatement([getModel, open_sub, removeLabel, calc_fingerprint, close_sub, add_label_again, return_results])
