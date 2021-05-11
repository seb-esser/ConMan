from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class GraphPath:

    def __init__(self, segments):
        self.segments = segments

    @classmethod
    def from_neo4j_response(cls, raw: str):
        """
        creates a graph path instance from a given neo4j response
        @param raw:
        @return:
        """
        # decode cypher response
        raw_path = raw[0][0]
        raw_nodes = raw[0][1]
        raw_edges = raw[0][2]

        nodes = NodeItem.fromNeo4jResponse(raw_nodes)
        edges = EdgeItem.from_neo4j_response(raw_edges, nodes)

        return cls(edges)

    def __repr__(self):
        return 'GraphPath instance'

    def to_patch(self, node_var: str = 'n', entry_node_identifier: str = None):
        """
        serializes the GraphPath object into a string representation
        @param node_var: identifier used inside a graph path
        @type entry_node_identifier: str representation of the entry node. use cypher style
        @return:
        """

        val = ''
        it = 1

        if entry_node_identifier is not None:
            start_node = entry_node_identifier
        else:
            start_node = self.segments[0].startNode.entityType

        val = '({})'.format(start_node)

        for edge in self.segments:
            relType = edge.relType
            end = edge.endNode.entityType
            val = val + '-[:{3}]->({0}{1} {{entityType: \'{2}\' }})'.format(node_var, it, end, relType)
            it += 1
        return val
