
""" package """
import itertools

""" modules """
from neo4jGraphDiff.ConfiguratorEnums import MatchCriteriaEnum


class SetCalculator(object):
	"""
	some utilities to calculate set operations on two given node sets
	"""

	def __init__(self):
		pass

	def compare_nodes(self, set_A: list, set_B: list, intersection_method: MatchCriteriaEnum):
		"""
		Calculates the boolean intersection between two node sets and returns the intersection set + the diff sets
		@param set_A: a (distinct) node set A
		@param set_B: a (distinct) node set B
		@param intersection_method: criteria on which the intersection is applied
		@return: three lists intersection, diffA, diffB
		"""
		# ToDo: react if hashes occur multiple times in the nodes_lists

		nodes_unchanged = []

		# match nodes based on child node hash
		A = set_A
		B = set_B

		# calculate matching pairs
		switcher = {
			MatchCriteriaEnum.OnGuid				: self.__get_intersection_byGlobalId(A, B),
			MatchCriteriaEnum.OnRelType				: self.__get_intersection_byRelType(A, B),
			MatchCriteriaEnum.OnEntityType			: self.__get_intersection_byEntityType(A, B),
			MatchCriteriaEnum.OnHash				: self.__get_intersection_byHash(A, B),
			MatchCriteriaEnum.OnHashAndOnRelType	: self.__get_intersection_byHashAnRelType(A, B)
		}

		matched_pairs = switcher[intersection_method]
						
		nodes_added = set_B
		nodes_deleted = set_A

		for pair in matched_pairs:
			nodes_added.remove(pair[1])
			nodes_deleted.remove(pair[0])
			nodes_unchanged.append((pair[0], pair[1]))	
		
		return nodes_unchanged, nodes_added, nodes_deleted

	# ---- Matching rules ---- 

	def __get_intersection_byHash(self, A, B):
		"""
		Calculates the boolean intersection between set A and set B by comparing the items' hashsums
		@param A: a (distinct) set of nodes
		@param B: a (distinct) set of nodes
		@return: a list of tuples as the result of the intersection operation
		"""
		return ((x, y) for x, y in itertools.product(A, B) if x.hash == y.hash)

	def __get_intersection_byHashAnRelType(self, A, B):
		"""
		Calculates the boolean intersection between set A and set B by comparing the items' hashsums and relTypes
		@param A: a (distinct) set of nodes
		@param B: a (distinct) set of nodes
		@return: a list of tuples as the result of the intersection operation
		"""
		return ((x, y) for x, y in itertools.product(A, B) if x.hash == y.hash and x.relType == y.relType)

	def __get_intersection_byRelType(self, A, B):
		"""
		Calculates the boolean intersection between set A and set B by comparing the relTypes
		@param A: a (distinct) set of nodes
		@param B: a (distinct) set of nodes
		@return: a list of tuples as the result of the intersection operation
		"""
		return ((x ,y) for x ,y in itertools.product(A, B) if x.relType == y.relType)

	def __get_intersection_byEntityType(self, A, B):
		"""
		Calculates the boolean intersection between set A and set B by comparing the items' entity types
		@param A: a (distinct) set of nodes
		@param B: a (distinct) set of nodes
		@return: a list of tuples as the result of the intersection operation
		"""
		return ((x, y) for x, y in itertools.product(A, B) if x.entityType == y.entityType)

	def __get_intersection_byEntityTypeAndRelType(self, A, B):
		"""
		Calculates the boolean intersection between set A and set B by comparing the items' entity types and rel types
		@param A: a (distinct) set of nodes
		@param B: a (distinct) set of nodes
		@return: a list of tuples as the result of the intersection operation
		"""
		return ((x, y) for x, y in itertools.product(A, B) if x.entityType == y.entityType and x.relType == y.relType)

	def __get_intersection_byGlobalId(self, A, B):
		"""
		Calculates the boolean intersection between set A and set B by comparing the items' global_ids
		@param A: a (distinct) set of nodes
		@param B: a (distinct) set of nodes
		@return: a list of tuples as the result of the intersection operation
		"""
		return ((x, y) for x, y in itertools.product(A, B) if x.attrs['GlobalId'] == y.attrs['GlobalId'])