""" package """
import itertools

from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum

""" modules """


class SetCalculator(object):
    """
    some utilities to calculate set operations on two given node sets
    """

    def __init__(self):
        pass

    def calc_intersection(self, set_A: list, set_B: list, intersection_method: MatchCriteriaEnum):
        """
        Calculates the boolean intersection between two node sets and returns the intersection set + the diff sets
        @param set_A: a (distinct) node set A
        @param set_B: a (distinct) node set B
        @param intersection_method: criteria on which the intersection is applied
        @return: three lists intersection, diffA, diffB
        """
        # ToDo: react if hashes occur multiple times in the nodes_lists

        nodes_unchanged = []

        # if len(set_A) == 0 or len(set_B) == 0:
            # raise Exception("got empty sets in set intersection calculation. ")


        # match nodes based on child node hash_value
        A = set_A
        B = set_B

        # calculate matching pairs
        switcher = {
            MatchCriteriaEnum.OnGuid: self.__get_intersection_byGlobalId(A, B),
            MatchCriteriaEnum.OnRelType: self.__get_intersection_byRelType(A, B),
            MatchCriteriaEnum.OnEntityType: self.__get_intersection_byEntityType(A, B),
            MatchCriteriaEnum.OnHash: self.__get_intersection_byHash(A, B),
            MatchCriteriaEnum.OnHashAndOnRelType: self.__get_intersection_byHashAnRelType(A, B)
        }

        matched_pairs = switcher[intersection_method]

        nodes_added = set_B
        nodes_deleted = set_A

        try:
            for pair in matched_pairs:
                nodes_added.remove(pair[1])
                nodes_deleted.remove(pair[0])
                nodes_unchanged.append((pair[0], pair[1]))
        except:
            print('A problem occured during set calculations. Tried to continue')
            # raise Exception('Unable to sort nodes in SetCalculator. ')

        return nodes_unchanged, nodes_added, nodes_deleted

    def calc_cartesian_product(self, set_a: list, set_b: list) -> list:
        """
        calculates the cartesian product between two given sets
        @param set_a:
        @param set_b:
        @return: a list of tuples
        """
        return [(a, b) for a in set_a for b in set_b]

    # ---- Matching rules ----

    def __get_intersection_byHash(self, A, B):
        """
        Calculates the boolean intersection between set A and set B
        by comparing the items' hashes
        @param A: a (distinct) set of nodes
        @param B: a (distinct) set of nodes
        @return: a list of tuples as the result of the intersection operation
        """
        return ((x, y) for x, y in itertools.product(A, B) if x.hash_value == y.hash_value)

    def __get_intersection_byHashAnRelType(self, A, B):
        """
        Calculates the boolean intersection between set A and set B
        by comparing the items' hashes and relTypes
        @param A: a (distinct) set of nodes
        @param B: a (distinct) set of nodes
        @return: a list of tuples as the result of the intersection operation
        """
        return ((x, y) for x, y in itertools.product(A, B) if x.hash_value == y.hash_value and x.relType == y.relType)

    def __get_intersection_byRelType(self, A, B):
        """
        Calculates the boolean intersection between set A and set B by comparing the relTypes
        @param A: a (distinct) set of nodes
        @param B: a (distinct) set of nodes
        @return: a list of tuples as the result of the intersection operation
        """
        return( ( x ,y) for x ,y in itertools.product(A, B) if x.relType == y.relType)

    def __get_intersection_byEntityType(self, A, B):
        """
        Calculates the boolean intersection between set A and set B
        by comparing the items' entity types
        @param A: a (distinct) set of nodes
        @param B: a (distinct) set of nodes
        @return: a list of tuples as the result of the intersection operation
            """
        return ((x, y) for x, y in itertools.product(A, B) if x.entityType == y.entityType)

    def __get_intersection_byEntityTypeAndRelType(self, A, B):
        """
        Calculates the boolean intersection between set A and set B
        by comparing the items' entity types and rel types
        @param A: a (distinct) set of nodes
        @param B: a (distinct) set of nodes
        @return: a list of tuples as the result of the intersection operation
            """
        return ((x, y) for x, y in itertools.product(A, B) if x.entityType == y.entityType and x.relType == y.relType)

    def __get_intersection_byGlobalId(self, A, B):
        """
        Calculates the boolean intersection between set A and set B
        by comparing the items' global_ids
        @param A: a (distinct) set of nodes
        @param B: a (distinct) set of nodes
        @return: a list of tuples as the result of the intersection operation
            """
        return ((x, y) for x, y in itertools.product(A, B) if x.attrs['GlobalId'] == y.attrs['GlobalId'])
