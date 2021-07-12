from typing import List

from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class NodeMatchingTable:

    def __init__(self):
        self.matched_nodes: List[NodePair] = []

    def add_matched_nodes(self, node1: NodeItem, node2: NodeItem):
        self.matched_nodes.append(NodePair(node1, node2))
        

class NodePair:
    def __init__(self, init: NodeItem, updated: NodeItem):
        self.init_node = init
        self.updated_node = updated
