from typing import List

from neo4j_middleware import neo4jConnector
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPath import GraphPath
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class GraphPattern:
    def __init__(self, paths):
        self.paths: List[GraphPath] = paths
        self.entry_node: NodeItem

    def __repr__(self):
        return 'GraphPattern instance composed by several GraphPath instances'

    @classmethod
    def from_neo4j_response(cls, raw):
        # decode cypher response
        raw_paths = raw

        paths = []

        for path in raw_paths:
            wrapper = [path]
            path = GraphPath.from_neo4j_response(wrapper)
            paths.append(path)

        return cls(paths)

    def load_rel_attrs(self, connector: neo4jConnector):
        """
        loads all attributes attached to each segment in the graph pattern
        @return: connected neo4j connector instance
        """
        for path in self.paths:
            for segment in path.segments:
                edge_id = segment.edge_id
                cy = Neo4jQueryFactory.get_relationship_attributes(edge_id)
                attr_dict = connector.run_cypher_statement(cy, 'PROPERTIES(r)')[0]
                segment.attributes = attr_dict

    def to_cypher_query(self):
        """
        creates a cypher query snippet to search for this pattern in a given graph
        @return:
        """

        alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                    'k', 'l', 'm', 'n', 'o', 'path', 'q', 'r']

        cy_statement: str = ""
        path_iterator = 0
        for path in self.paths:
            cy_path = path.to_patch(node_var=alphabet[path_iterator], entry_node_identifier='en', path_number=path_iterator)
            cy_statement = cy_statement + ' {}'.format(cy_path)
            path_iterator += 1

        return cy_statement

    def get_number_of_paths(self) -> int:
        """
        returns the number of paths in the pattern
        @return:
        """
        return len(self.paths)
