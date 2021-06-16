from typing import List

from neo4j_middleware import neo4jConnector
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
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

    def to_cypher_query(self, timestamp: str = None) -> str:
        """
        creates a cypher query snippet to search for this pattern in a given graph
        @return: cypher statement snippet
        """

        alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                    'k', 'l', 'm', 'n', 'o', 'path', 'q', 'r']

        cy_statement: str = ""
        path_iterator = 0
        for path in self.paths:
            cy_paths = path.to_patch(node_var=alphabet[path_iterator], entry_node_identifier='en', path_number=path_iterator)
            cy_path = " ".join(cy_paths)

            cy_statement = cy_statement + ' {}'.format(cy_path)
            path_iterator += 1

        return cy_statement

    def to_cypher_query_indexed(self, timestamp: str = None) -> str:
        """
        improved version to search for a specified graph pattern using a distinct node set definition
        @type timestamp: optional timestamp string to identify the target graph the pattern should be searched for
        @return:
        """

        all_nodes: List[NodeItem] = self.get_unified_node_set()
        self.get_unified_edge_set()

        node_dict = {}
        for n in all_nodes:
            if timestamp is None:
                node_dict[n.id] = 'n{}'.format(n.id)
            else:
                node_dict[n.id] = 'n{}: {}'.format(n.id, timestamp)

        # init cypher query
        cy_list = []

        path_iterator = 0
        # loop over all paths. Each path contains a list of segments
        for unified_path in self.paths:
            # build start of cypher subquery
            start = unified_path.segments[0].startNode
            # cy_list.append('MATCH path{0} = ({1})'.format(path_iterator, node_dict[start.id]))

            cy_start = 'MATCH path{0} = {1}'.format(path_iterator, start.to_cypher(node_identifier=node_dict[start.id]))
            cy_list.append(cy_start)

            # define path section
            edge_iterator = 0
            for edge in unified_path.segments:

                end = edge.endNode
                cy_frag = edge.to_cypher_fragment(
                    target_identifier=node_dict[end.id],
                    segment_identifier=path_iterator,
                    relationship_iterator=edge_iterator)
                cy_list.append(cy_frag)
                edge_iterator += 1

            # increase path iterator by one
            path_iterator += 1
            cy_list.append(' ')

        cy_statement = ''.join(cy_list)

        return cy_statement

    def to_cypher_create(self, timestamp: str = None) -> str:
        """
        creates a cypher query string to create a given graph pattern in a target graph
         without recognizing existing items
        @param timestamp:
        @return:
        """

        all_nodes: List[NodeItem] = self.get_unified_node_set()
        self.get_unified_edge_set()

        node_dict = {}
        for n in all_nodes:
            node_dict[n.id] = 'n{}'.format(n.id)

        # init cypher query
        cy_list = []

        # in CREATE statements, each node can be created only once.
        # therefore, re-use its var name but do not re-create attributes etc

        # 1: create all nodes
        for node in all_nodes:
            cy_node = node.to_cypher(timestamp=timestamp, node_identifier=node_dict[node.id])
            cy_frag = 'CREATE {} '.format(cy_node)
            cy_list.append(cy_frag)

        # 2: create all paths

        # from here on: only use the node variables stated in the node_dict.
        # All nodes and their attributes are already created
        path_iterator = 0
        # loop over all paths. Each path contains a list of segments
        for unified_path in self.paths:
            # build start of cypher subquery
            start = unified_path.segments[0].startNode
            # cy_list.append('MATCH path{0} = ({1})'.format(path_iterator, node_dict[start.id]))

            cy_start = 'CREATE path{0} = ({1})'.format(path_iterator, node_dict[start.id])
            cy_list.append(cy_start)

            # define path section
            edge_iterator = 0
            for edge in unified_path.segments:
                end = edge.endNode
                cy_frag = edge.to_cypher_create(
                    target_identifier=node_dict[end.id],
                    segment_identifier=path_iterator,
                    relationship_iterator=edge_iterator)
                cy_list.append(cy_frag)
                edge_iterator += 1

            # increase path iterator by one
            path_iterator += 1
            cy_list.append(' ')

        cy_statement = ''.join(cy_list)

        return cy_statement

    def get_number_of_paths(self) -> int:
        """
        returns the number of paths in the pattern
        @return:
        """
        return len(self.paths)

    def get_unified_node_set(self) -> List[NodeItem]:
        """
        returns a unified/distinct list of nodes of the graph pattern
        @return: unified list of nodes
        """
        unified_pattern_node_list = []
        for path in self.paths:
            for segment in path.segments:
                start_node = segment.startNode
                end_node = segment.endNode
                if start_node not in unified_pattern_node_list:
                    unified_pattern_node_list.append(start_node)
                if end_node not in unified_pattern_node_list:
                    unified_pattern_node_list.append(end_node)
        return unified_pattern_node_list

    def get_unified_edge_set(self):
        """
        unifies the set of edges included in the graph pattern.
        @return:
        """
        # print before state to console
        # self.print_to_console()

        unified_segments = []
        # loop over all paths
        for path in self.paths:
            # a path consists of several segments (i.e., edges)
            initial_segments = list(path.segments)  # make deep copy
            for segment in initial_segments:

                if segment.edge_id in unified_segments:
                    # segment has been already tackled
                    # remove current segment from Path
                    path.remove_segments_by_id([segment.edge_id])
                else:
                    # segment appears the first time, therefore keep it and add it to the list
                    unified_segments.append(segment.edge_id)

        # print after state to console
        # self.print_to_console()

    def print_to_console(self):
        """
        visualizes the graph pattern structure to the console
        @return:
        """
        print('GraphPattern structure: ')
        no = 0
        for path in self.paths:
            print('\t path no {}:'.format(no))
            no += 1
            for seg in path.segments:
                print('\t\t{}'.format(str(seg)))
