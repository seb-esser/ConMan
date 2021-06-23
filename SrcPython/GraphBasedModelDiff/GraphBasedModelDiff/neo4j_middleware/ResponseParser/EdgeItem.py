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

    def to_cypher(self, source_identifier: str, target_identifier: str) -> str:
        """
        returns a cypher statement to search for this edge item.
        @param source_identifier:
        @param target_identifier:
        @return: cypher statement as str
        """
        cy = 'MATCH {0}-[rel{1}]->{2}'.format(
            self.startNode.to_cypher(timestamp=None, node_identifier=source_identifier),
            Neo4jFactory.formatDict(self.attributes),
            self.endNode.to_cypher(timestamp=None, node_identifier=target_identifier))
        return cy

    def to_cypher_fragment(self, target_identifier: str, segment_identifier: int, relationship_iterator: int) -> str:
        """
        returns a fragment of a cypher statement to assemble several edges to a path
        @param target_identifier:
        @param segment_identifier:
        @param relationship_iterator:
        @return: cypher fragment as str
        """
        cy = '-[r{3}{2}{0}]->{1}'.format(
            Neo4jFactory.formatDict(self.attributes),
            self.endNode.to_cypher(timestamp=None, node_identifier=target_identifier),
            relationship_iterator, segment_identifier)
        return cy

    def to_cypher_create(self, target_identifier: str, segment_identifier: int, relationship_iterator: int):
        """
        returns a cypher command to create the edge. the edge is labeled with 'rel'
        @return: cypher statement as str
        """
        cy = '-[r{3}{2}:rel{0}]->({1})'.format(
            Neo4jFactory.formatDict(self.attributes),
            target_identifier,
            relationship_iterator,
            segment_identifier)
        return cy

    def to_cypher_merge(self, target_identifier: str, target_node: NodeItem, target_timestamp: str, segment_identifier: int, relationship_iterator: int):
        """
        returns a cypher command to create the edge. the edge is labeled with 'rel'
        @return: cypher statement as str
        """
        cy = '-[r{3}{2}:rel{0}]->{1}'.format(
            Neo4jFactory.formatDict(self.attributes),
            target_node.to_cypher(timestamp=target_timestamp, node_identifier=target_identifier, include_nodeType_label=True),
            relationship_iterator,
            segment_identifier)
        return cy



