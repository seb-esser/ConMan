


class DiffUtilities:
	""" """ 
	
	def __init__(self):
		pass

	def GetHashes(self, label):
		getModel = 'MATCH(n:rootedNode:{})'.format(label)
		open_sub = 'CALL {WITH n'
		removeLabel = 'REMOVE n:{}'.format(label)
		calc_fingerprint = 'with APOC.hashing.fingerprint(n) as hash RETURN hash'
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
		calc_fingerprint = 'with APOC.hashing.fingerprint(n) as hash RETURN hash'

		fingerprint_with_ign = 'with APOC.hashing.fingerprint(n, {}) as hash RETURN hash'.format('[p21_id]')

		close_sub = '}'
		add_label_again = 'SET n:{}'.format(label)
		return_results = 'RETURN hash, n.entityType, ID(n)'
		return [getModel, where, open_sub, removeLabel, calc_fingerprint, close_sub, add_label_again, return_results]



