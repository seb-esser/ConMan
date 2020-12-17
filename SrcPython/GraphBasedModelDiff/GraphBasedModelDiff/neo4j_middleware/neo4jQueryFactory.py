

class neo4jQueryFactory: 

	def __init__(self): 
		pass

	@classmethod
	def DiffNodes(cls, nodeIDleft, nodeIDright):
		query_left = 'MATCH l WHERE ID(l) = {}'.format(nodeIDleft)
		query_right = 'MATCH r WHERE ID(r) = {}'.format(nodeIDright)
		ret_statement = 'RETURN apoc.diff.nodes(l,r)'


