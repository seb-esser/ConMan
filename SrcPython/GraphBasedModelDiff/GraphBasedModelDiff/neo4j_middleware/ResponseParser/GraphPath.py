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
        segments = EdgeItem.from_neo4j_response(raw_edges, nodes)

        return cls(segments)

    def __repr__(self):
        return 'GraphPath instance'

    def to_patch(self, node_var: str = 'n', entry_node_identifier: str = None, path_number: int = None):
        """
        serializes the GraphPath object into a string representation
        @param path_number: specify an integer indicating the path number inside a pattern. Otherwise None
        @param node_var: identifier used inside a graph path
        @type entry_node_identifier: str representation of the entry node. use cypher style
        @return:
        """

        # init local vars of this method
        cy = ''
        segment_iterator = 1

        if entry_node_identifier is not None:
            start_node = entry_node_identifier
        else:
            start_node = self.segments[0].startNode.entityType

        # init cypher statement
        if path_number is not None:
            cy = 'MATCH path{} = ({})'.format(path_number, start_node)
        else:
            cy = 'MATCH ({})'.format(segment_iterator, start_node)

        # loop over all segments of the current path
        for segment in self.segments:
            end = segment.endNode.entityType
            rel_attrs = segment.attributes

            def format_rel_attrs(attrs: dict):
                cy = '{'
                for key, val in attrs.items():
                    cy = cy + key + ': ' + val
                cy = cy + '}'
                return cy

            cy = cy + '-[r{1}{4} {3} ]->({0}{1} {{EntityType: \'{2}\' }})'\
                .format(node_var, segment_iterator, end, self.formatDict(rel_attrs), path_number)
            segment_iterator += 1
        return cy

    def formatDict(self, dictionary):
        """
        formats a given dictionary to be understood in a cypher query
        @param dictionary: dict to be formatted
        @return: string representation of dict
        """

        # copied and tweaked from: https://stackoverflow.com/a/65346803
        s = "{"

        for key in dictionary:
            s += "{0}:".format(key)
            if isinstance(dictionary[key], dict):
                # Apply formatting recursively
                s += "{0}, ".format(dictionary(self[key]))
            elif isinstance(dictionary[key], list):
                s += "["
                for l in dictionary[key]:
                    if isinstance(l, dict):
                        s += "{0}, ".format(dictionary(l))
                    else:
                        # print(l)
                        if isinstance(l, int):
                            s += "{0}, ".format(l)
                        else:
                            s += "'{0}', ".format(l)
                if len(s) > 1:
                    s = s[0: -2]
                s += "], "
            else:
                if isinstance(dictionary[key], int):
                    s += "{0}, ".format(dictionary[key])
                else:
                    s += "\'{0}\', ".format(dictionary[key])
                # Quote all the values
                # s += "\'{0}\', ".format(self[key])

        if len(s) > 1:
            s = s[0: -2]
        s += "}"
        return s
