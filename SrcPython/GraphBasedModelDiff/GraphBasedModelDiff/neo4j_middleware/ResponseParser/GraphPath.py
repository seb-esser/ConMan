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

    def to_patch(self):
        """
        serializes the GraphPath object into a string representation
        @return:
        """

        val = ''
        for edge in self.segments:
            start = edge.startNode.entityType
            relType = edge.relType
            val = val + '({})-[:{}]->'.format(start, relType)

        val = val + '({})'.format(self.segments[-1].endNode.entityType)

        return val
