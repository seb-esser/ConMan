

""" package """
import itertools

""" modules """
from .DiffIgnore_parser import DiffIgnore
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities


class DiffUtilities:
	""" """ 
	
	def __init__(self, diffIgnorePath = None):

		if diffIgnorePath != None: 
			self.diffIngore = DiffIgnore.from_json(diffIgnorePath)

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

	
