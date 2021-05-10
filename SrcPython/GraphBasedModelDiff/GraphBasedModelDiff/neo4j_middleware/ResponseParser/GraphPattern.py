from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
from neo4j_middleware.ResponseParser.GraphPath import GraphPath


class GraphPattern:
    def __init__(self, paths):
        self.paths : list[GraphPath] = paths

    @classmethod
    def from_neo4j_response(cls, raw):
        # decode cypher response
        raw_paths = raw

        paths = []

        for path in raw_paths:
            print(path.start)
            path = GraphPath.from_neo4j_response(path)
            paths.append(path)

        return cls(paths)

