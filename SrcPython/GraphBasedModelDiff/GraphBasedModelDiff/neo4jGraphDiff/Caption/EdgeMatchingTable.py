from typing import List

from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem


class EdgeMatchingTable:

    def __init__(self):
        self.matched_nodes: List[EdgePair] = []

    def add_matched_nodes(self, edge1: EdgeItem, edge2: EdgeItem):
        self.matched_nodes.append(EdgePair(edge1, edge2))


class EdgePair:
    def __init__(self, init: EdgeItem, updated: EdgeItem):
        self.init_node = init
        self.updated_node = updated
