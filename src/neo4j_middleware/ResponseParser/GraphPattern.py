from typing import List

from neo4j_middleware import neo4jConnector
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPath import GraphPath
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class GraphPattern:
    def __init__(self, paths):
        self.paths: List[GraphPath] = paths

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

    def get_entry_node(self) -> NodeItem:
        """
        returns the entry node of this graphPattern
        @return: NodeItem reflecting the entry node of this pattern
        """
        return self.paths[0].get_start_node()

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

        include_primary_paths = True
        if include_primary_paths:
            prm_paths = self.query_primary_paths()
            cy_list += prm_paths

        define_return = True
        if define_return:
            num_paths = self.get_number_of_paths()
            try:
                num_primPaths = len(prm_paths)
            except:
                num_primPaths = 0

            return_cy = 'RETURN '
            for np in range(num_paths):
                return_cy += 'path{}, '.format(np)
            for npr in range(num_primPaths):
                return_cy += 'primPath{}, '.format(npr)
            return_cy = return_cy[:-2] # remove last ', '

            cy_list.append(return_cy)

        # build the final cypher statement
        cy_statement = ''.join(cy_list)

        return cy_statement

    def to_cypher_create(self, timestamp: str = None, reference_structure = None) -> str:
        """
        creates a cypher query string to create a given graph pattern in a target graph
         without recognizing existing items
        @param reference_structure:
        @param timestamp:
        @return: cypher query statement as str
        """

        all_nodes: List[NodeItem] = self.get_unified_node_set()
        self.get_unified_edge_set()

        node_dict = {}
        for n in all_nodes:
            node_dict[n.id] = 'n{0}'.format(n.id, n.nodeType)

        # init cypher query
        cy_list = []

        if reference_structure is not None:
            match_reference = reference_structure.to_cypher_indexed()
            cy_list.append(match_reference)

        # in CREATE statements, each node can be created only once.
        # therefore, re-use its var name but do not re-create attributes etc

        # 1: create all nodes
        for node in all_nodes:
            cy_node = node.to_cypher(timestamp=timestamp, node_identifier=node_dict[node.id], include_nodeType_label=True)
            cy_frag = 'MERGE {} '.format(cy_node)
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

    def to_cypher_merge(self, timestamp: str = None) -> str:
        """
        creates a cypher query string to create a given graph pattern in a target graph
        without recognizing existing items
        @param timestamp:
        @return: cypher query statement as str
        """

        all_nodes: List[NodeItem] = self.get_unified_node_set()
        self.get_unified_edge_set()

        node_dict = {}
        for n in all_nodes:
            node_dict[n.id] = 'n{0}'.format(n.id, n.nodeType)

        # init cypher query
        cy_list = []

        # from here on: only use the node variables stated in the node_dict.
        # All nodes and their attributes are already created
        path_iterator = 0
        # loop over all paths. Each path contains a list of segments
        for unified_path in self.paths:
            # build start of cypher subquery
            start = unified_path.segments[0].startNode
            # cy_list.append('MATCH path{0} = ({1})'.format(path_iterator, node_dict[start.id]))
            edge_iterator = 0
            for edge in unified_path.segments:
                startNode = edge.startNode
                endNode = edge.endNode
                cy = 'MERGE {}'.format(edge.startNode.to_cypher(timestamp=timestamp,
                                                                   node_identifier='a{}{}'.format(
                                                                       path_iterator,
                                                                       edge_iterator),
                                                                   include_nodeType_label=True))\
                     + edge.to_cypher_merge(
                    target_node=endNode,
                    target_identifier='b{}{}'.format(path_iterator,edge_iterator),
                    target_timestamp=timestamp,
                    segment_identifier=path_iterator,
                    relationship_iterator=edge_iterator)
                cy_list.append(cy)
                edge_iterator += 1

            # increase path iterator by one
            path_iterator += 1
            cy_list.append(' ')

        cy_statement = ''.join(cy_list)

        return cy_statement

    def to_cypher_merge_separated(self, timestamp: str = None) -> str:
        """
        creates a cypher query string to create a given graph pattern in a target graph
        without recognizing existing items
        @param timestamp:
        @return: cypher query statement as str
        """

        all_nodes: List[NodeItem] = self.get_unified_node_set()
        self.get_unified_edge_set()

        node_dict = {}
        for n in all_nodes:
            node_dict[n.id] = 'n{0}'.format(n.id, n.nodeType)

        # init cypher query
        cy_list = []

        # 2: create all paths

        # from here on: only use the node variables stated in the node_dict.
        # All nodes and their attributes are already created
        path_iterator = 0
        # loop over all paths. Each path contains a list of segments
        for unified_path in self.paths:
            # build start of cypher subquery
            edge_iterator = 0
            for edge in unified_path.segments:
                cy = edge.to_cypher_individual_merge(target_timestamp=timestamp,
                                                segment_identifier=path_iterator,
                                                relationship_iterator=edge_iterator)
                print(cy)

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
        return self.paths

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

    def split_pattern(self):
        """
        removes the current entry node from the pattern and returns the sub-patterns
        @return:
        """
        node = self.get_entry_node()

        sub_patterns: List[GraphPattern] = []
        new_start_nodes = []
        # find edges the current node is involved
        for path in self.paths:
            if path.get_start_node() == node:

                # remove first segment from current path
                cutted_path = path.segments[1:]
                path_object = GraphPath(cutted_path)

                new_start_node = cutted_path[0].startNode
                if new_start_node not in new_start_nodes:
                    pattern = GraphPattern([path_object])
                    sub_patterns.append(pattern)
                    new_start_nodes.append(new_start_node)
                else:
                    # find pattern that has the same start node as the current cutted_path
                    sub_p = [x for x in sub_patterns if x.get_entry_node() == new_start_node][0]
                    sub_p.paths.append(path_object)

        return sub_patterns

    def query_primary_paths(self):
        unified_nodes = self.get_unified_node_set()
        cy_list = []
        it = 0
        for n in unified_nodes:
            cy = 'OPTIONAL MATCH refPath{0} = (n{1})--(refNode{1}) '.format(it, n.id)
            cy_list.append(cy)
            it += 1
        return cy_list

    def tidy_node_attributes(self):
        """
        removes all p21_id attributes from nodes involved in this pattern
        @return:
        """
        for p in self.paths:
            for e in p.segments:
                n1: NodeItem = e.startNode
                n2: NodeItem = e.startNode
                n1.tidy_attrs(remove_None_values=False)
                n2.tidy_attrs(remove_None_values=False)

    def compare_pattern(self, other):
        """

        @param other:
        @return:
        """

        return False


