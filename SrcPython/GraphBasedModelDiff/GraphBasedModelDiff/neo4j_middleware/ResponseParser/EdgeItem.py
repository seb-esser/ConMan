from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class EdgeItem:
    def __init__(self, start_node: NodeItem, end_node: NodeItem, relType: str):
        self.relType: str = relType
        self.startNode: NodeItem = start_node
        self.endNode: NodeItem = end_node

    @classmethod
    def from_neo4j_response(cls, raw: str, nodes: list):
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
            raw_type = edge.type

            start_node = (x for x in nodes if x.id == raw_startnode_id)
            end_node = (x for x in nodes if x.id == raw_endnode_id)

            e = cls(start_node, end_node, raw_type)
            edges.append(e)

        return edges

