from typing import List

from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class NodeMatchingTable:

    def __init__(self):
        self.matched_nodes: List[NodePair] = []

    def add_matched_nodes(self, node1: NodeItem, node2: NodeItem):
        """
        appends a single NodePair instance to the list and checks existence upfront
        @param node1:
        @param node2:
        @return:
        """
        pair = NodePair(node1, node2)
        if pair not in self.matched_nodes:
            self.matched_nodes.append(pair)

    def append_pairs(self, matchedNodes):
        """
        appends a list of NodePair items and checks if they already exist in the parent list
        @param matchedNodes:
        @return:
        """
        for pair in matchedNodes.matched_nodes:
            if pair not in self.matched_nodes:
                self.matched_nodes.append(pair)

    def get_all_init_nodes(self):
        return [x.init_node for x in self.matched_nodes]

    def get_all_updated_nodes(self):
        return [x.updated_node for x in self.matched_nodes]

    def node_involved_in_nodePair(self, node: NodeItem):
        """
        returns true if nodeItem is captured within a node pair
        @param node:
        @return:
        """
        if node in self.get_all_init_nodes():
            return True
        elif node in self.get_all_updated_nodes():
            return True
        else:
            return False

    def node_pair_in_matching_table(self, pair):
        """
        returns true if a NodePair item is already listed in the matching table
        @param pair:
        @return:
        """
        if pair in self.matched_nodes:
            return True
        else:
            return False


class NodePair:
    def __init__(self, init: NodeItem, updated: NodeItem):
        self.init_node: NodeItem = init
        self.updated_node: NodeItem = updated

    def __repr__(self):
        return 'NodePair: entityType: {} ID_init: {} ID_updated: {}'.format(
            self.init_node.entityType,
            self.init_node.id,
            self.updated_node.id)