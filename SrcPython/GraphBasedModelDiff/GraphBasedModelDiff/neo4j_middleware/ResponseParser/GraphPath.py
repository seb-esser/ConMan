from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
from neo4j_middleware.ResponseParser.NodeItem import NodeItem

class GraphPath:

    def __init__(self):
        self.segments: list(PathSegment)

    @classmethod
    def from_neo4j_response(cls, raw: str):
        # decode cypher response
        raw_path = raw[0][0]
        raw_nodes = raw[0][1]
        raw_edges = raw[0][2]

        nodes = NodeItem.fromNeo4jResponse(raw_nodes)
        edges = EdgeItem.from_neo4j_response(raw_edges, nodes)

        rels = raw[0].relationships
        # loop over all path items
        for rel in rels:
            raw_startnode_id = rel.start_node.id
            raw_endnode_id = rel.end_node.id
            raw_type = rel.type

            segment = PathSegment()


class PathSegment:
    def __init__(self):
        self.start: NodeItem
        self.end: NodeItem
        self.relType: str