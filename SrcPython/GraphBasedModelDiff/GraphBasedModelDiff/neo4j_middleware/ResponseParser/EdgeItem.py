from neo4j_middleware.ResponseParser import NodeItem
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory


class EdgeItem:
    def __init__(self, start_node: NodeItem, end_node: NodeItem, rel_id: int):
        self.startNode = start_node
        self.endNode = end_node
        self.edge_id = rel_id
        self.attributes: dict = {}

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

