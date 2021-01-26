

""" package """
import itertools

""" modules """
from .DiffIgnore_parser import DiffIgnore
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities
from neo4jGraphDiff.ConfiguratorEnums import MatchCriteriaEnum


class DiffUtilities:
	""" """ 
	
	def __init__(self):
		pass

	def CompareNodes(self, nodes_init, nodes_updated, MatchingMethod):
		""" returns lists of unchangedNodes, addedNodes and deletedNodes according to the stated matchingMethod """

		# ToDo: react if hashes occure multiple times in the nodes_lists

		nodes_unchanged = []
		nodes_deleted = []
		nodes_added = []
				
		# match nodes based on child node hash
		A = nodes_init
		B = nodes_updated

		# calculate matching pairs
		switcher = {
			MatchCriteriaEnum.OnGuid				: self.__GetMatchingPairs_byGlobalId(A, B),
			MatchCriteriaEnum.OnRelType				: self.__GetMatchingPairs_byRelType(A, B),
			MatchCriteriaEnum.OnEntityType			: self.__GetMatchingPairs_byEntityType(A, B),
			MatchCriteriaEnum.OnHash				: self.__GetMatchingPairs_byHash(A, B), 
			MatchCriteriaEnum.OnHashAndOnRelType	: self.__GetMatchingPairs_byHashAnRelType(A, B)			
			}

		matched_pairs = switcher[MatchingMethod]
						
		nodes_added = nodes_updated
		nodes_deleted = nodes_init

		for pair in matched_pairs:
			nodes_added.remove(pair[1])
			nodes_deleted.remove(pair[0])
			nodes_unchanged.append((pair[0], pair[1]))	
		
		return nodes_unchanged, nodes_added, nodes_deleted


	# ---- Matching rules ---- 

	def __GetMatchingPairs_byHash(self, A, B):
		return ((x,y) for x,y in itertools.product(A, B) if x.hash == y.hash)

	def __GetMatchingPairs_byHashAnRelType(self, A, B):
		return ((x,y) for x,y in itertools.product(A, B) if x.hash == y.hash and x.relType == y.relType)

	def __GetMatchingPairs_byRelType(self, A, B):
		return ((x,y) for x,y in itertools.product(A, B) if x.relType == y.relType)

	def __GetMatchingPairs_byEntityType(self, A, B):
		return ((x,y) for x,y in itertools.product(A, B) if x.entityType == y.entityType)

	def __GetMatchingPairs_byEntityTypeAndRelType(self, A, B):
		return ((x,y) for x,y in itertools.product(A, B) if x.entityType == y.entityType and x.relType == y.relType)

	def __GetMatchingPairs_byGlobalId(self, A, B):
		# ToDo: ensure that nodes have the attrs value set
		return ((x,y) for x,y in itertools.product(A, B) if x.attrs['GlobalId'] == y.attrs['GlobalId'])

