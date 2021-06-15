from neo4j_middleware.ResponseParser import NodeItem
from neo4j_middleware.Neo4jFactory import Neo4jFactory


class EdgeItem:
    def __init__(self, start_node: NodeItem, end_node: NodeItem, rel_id: int):
        self.startNode: NodeItem = start_node
        self.endNode: NodeItem = end_node
        self.edge_id: int = rel_id
        self.attributes: dict = {}

    def __repr__(self):
        return 'EdgeItem object: startId: {} - edgeId: {} -> targetId: {}'\
            .format(self.startNode.id, self.edge_id, self.endNode.id)

    def __eq__(self, other):
        """
        compares two edges and returns true if both edges are considered as equal
        @param other:
        @return:
        """

        # start_equal = self.startNode == other.startNode
        # end_equal = self.endNode == other.endNode
        # rel_attrs_equal = self.attributes == other.attributes
        id_equal = self.edge_id == other.edge_id
        # if all([start_equal, end_equal, rel_attrs_equal]):
        return id_equal

    @classmethod
    def from_neo4j_response(cls, raw: str, nodes):
        """
        returns a list of EdgeItem instances from a given neo4j response string
        @raw: the neo4j response
        @nodes: a list of nodeItem instances
        @return: a list of EdgeItem instances in a list
        """

        edges = []

        for edge in raw:
            raw_startnode_id = edge.start_node.id
            raw_endnode_id = edge.end_node.id
            edge_id = edge.id

            start_node = next(x for x in nodes if x.id == raw_startnode_id)
            end_node = next(x for x in nodes if x.id == raw_endnode_id)

            e = cls(start_node, end_node, edge_id)
            edges.append(e)

        return edges

    def to_cypher(self, source_identifier: str, target_identifier: str):
        cy = 'MATCH {0}-[rel{1}]->{2}'.format(
            self.startNode.to_cypher(node_identifier=source_identifier, timestamp=None),
            Neo4jFactory.formatDict(self.attributes),
            self.endNode.to_cypher(node_identifier=target_identifier, timestamp=None))
        return cy

    def to_cypher_fragment(self, target_identifier: str, segment_identifier: int, relationship_iterator: int):
        cy = '-[r{3}{2}{0}]->{1}'.format(
            Neo4jFactory.formatDict(self.attributes),
            self.endNode.to_cypher(node_identifier=target_identifier, timestamp=None),
            relationship_iterator, segment_identifier)
        return cy