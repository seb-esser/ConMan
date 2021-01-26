

""" package """
import itertools

""" modules """
from .DiffIgnore_parser import DiffIgnore
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities


class DiffUtilities:
	""" """ 
	
	def __init__(self):
		pass

	def CompareNodesByHash(self, nodes_init, nodes_updated, considerRelType = True):
		# ToDo: react if hashes occure multiple times in the nodes_lists

		nodes_unchanged = []
		nodes_deleted = []
		nodes_added = []

		
		if not considerRelType:
			# match nodes based on child node hash
			A=nodes_init
			B=nodes_updated
			matched_pairs = ((x,y) for x,y in itertools.product(A, B) if x.hash == y.hash)
						
			nodes_added = nodes_updated
			nodes_deleted = nodes_init

			for pair in matched_pairs:
				nodes_added.remove(pair[1])
				nodes_deleted.remove(pair[0])
				nodes_unchanged.append((pair[0], pair[1]))

		else:
					
			# match nodes based on hash and reltype
			A = nodes_init
			B = nodes_updated
			matched_pairs = ((x,y) for x,y in itertools.product(A, B) if x.hash == y.hash and x.relType == y.relType)
						
			nodes_added = nodes_updated
			nodes_deleted = nodes_init

			for pair in matched_pairs:
				nodes_added.remove(pair[1])
				nodes_deleted.remove(pair[0])
				nodes_unchanged.append((pair[0], pair[1]))

		return nodes_unchanged, nodes_added, nodes_deleted

	def CompareNodesByGUID(self, nodes_init, nodes_updated):
		raise Exception('Method CompareNodesByGUID is not implemented yet')

	def CompareNodesByRelType(self, nodes_init, nodes_updated):
		raise Exception('Method CompareNodesByRelType is not implemented yet')

	def CompareNodesByNodeType(self, nodes_init, nodes_updated):
		raise Exception('Method CompareNodesByNodeType is not implemented yet')

	def CompareNodesByNodeTypeAndRelType(self, nodes_init, nodes_updated):
		raise Exception('Method CompareNodesByNodeTypeAndRelType is not implemented yet')
