from typing import List

from neo4jGraphDiff.Caption.NodeMatchingTable import NodeMatchingTable
from neo4j_middleware import neo4jConnector
from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem


class EdgeMatchingTable:

    def __init__(self):
        self.matched_edges: List[EdgePair] = []

    @classmethod
    def from_node_matching(cls, connector: neo4jConnector, matched_nodes: NodeMatchingTable):
        pass


class EdgePair:
    def __init__(self, init: EdgeItem, updated: EdgeItem):
        self.init_edge = init
        self.updated_edge = updated
