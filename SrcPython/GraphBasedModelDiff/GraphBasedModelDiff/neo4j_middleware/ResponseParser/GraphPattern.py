from neo4j_middleware.ResponseParser.GraphPath import GraphPath


class GraphPattern:
    def __init__(self, paths):
        self.paths: list[GraphPath] = paths

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

    def to_cypher_query(self, use_one_entry_node: bool = False):
        """

        @return:
        """

        alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r']

        cy_statement: str = ""
        path_iterator = 0
        for p in self.paths:
            cy_statement = ''
            cy_path = p.to_patch(node_var=alphabet[path_iterator])
            cy_statement = cy_statement + 'MATCH path{} = {} '.format(path_iterator, cy_path)

            print(cy_statement)
            path_iterator += 1
        return cy_statement
