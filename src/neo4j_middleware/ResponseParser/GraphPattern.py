from typing import List
import re

from neo4j_middleware import neo4jConnector
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
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

    @classmethod
    def from_cypher_statement(cls, cypher_statement: str):

        paths = []

        # ToDo: manage cases with multiple cypher lines
        # split into fragments
        fragments = cypher_statement.split('\n')
        # fragments = [cypher_statement]

        for cy_fragment in fragments:

            # pre-processing steps to make regex statements easier
            cy_fragment = cy_fragment.replace("--", "-[:]-")

            regex_nodes = r"\(([^]]+)\)"
            regex_edge_generic = r"(<?)-\[([^]]+)\]-(>?)"

            raw_nodes = re.findall(regex_nodes, cy_fragment, re.MULTILINE)
            raw_edges = re.findall(regex_edge_generic, cy_fragment, re.MULTILINE)

            # sorted list specific to currently processed cypher fragment
            node_collection = []
            edge_collection = []

            # loop over nodes
            i = 0
            for raw_node in raw_nodes:
                node = NodeItem.from_cypher_fragment(raw_node)
                node.id = i
                node_collection.append(node)
                i += 1

            counter_left = 0
            counter_right = 1
            edge_counter = 0
            for raw_edge in raw_edges:
                node_left = node_collection[counter_left]
                node_right = node_collection[counter_right]

                edge = EdgeItem.from_cypher_fragment(raw_edge, node_left, node_right)
                edge.edge_id = edge_counter
                edge_collection.append(edge)

                counter_left += 1
                counter_right += 1
                edge_counter += 1

            path = GraphPath(segments=edge_collection)
            paths.append(path)

        return cls(paths=paths)

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

    def to_cypher_match(self, timestamp: str = None) -> str:
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
            start = unified_path.segments[0].start_node
            # cy_list.append('MATCH path{0} = ({1})'.format(path_iterator, node_dict[start.id]))

            cy_start = 'MATCH path{0} = {1}'.format(path_iterator, start.to_cypher())
            cy_list.append(cy_start)

            # define path section
            edge_iterator = 0
            # todo: bridges the to_cypher() method of a graphPath instance
            for edge in unified_path.segments:

                end = edge.end_node
                cy_frag = edge.to_cypher(skip_start_node=True)
                # ToDo: to_cypher_fragment() has been deprecated and replaced by to_cypher.
                #  Use skip_start_node to achieve similar results than before
                cy_list.append(cy_frag)
                edge_iterator += 1

            # increase path iterator by one
            path_iterator += 1
            cy_list.append(' ')

        include_primary_paths = False
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

    def to_cypher_merge(self, reference_structure=None) -> str:
        """
        creates a cypher query string to create a given graph pattern in a target graph
         without recognizing existing items
        @param reference_structure:

        @return: cypher query statement as str
        """

        all_nodes: List[NodeItem] = self.get_unified_node_set()
        # self.get_unified_edge_set()

        node_dict = {}
        for n in all_nodes:
            node_dict[n.id] = 'n{0}'.format(n.id, n.get_node_type())

        # init cypher query
        cy_list = []

        if reference_structure is not None:
            match_reference = reference_structure.to_cypher_indexed()
            cy_list.append(match_reference)

        # in CREATE statements, each node can be created only once.
        # therefore, re-use its var name but do not re-create attributes etc

        # 1: create all nodes
        for node in all_nodes:
            cy_node = node.to_cypher()
            cy_frag = 'MERGE {} '.format(cy_node)
            cy_list.append(cy_frag)

        # 2: create all paths

        # from here on: only use the node variables stated in the node_dict.
        # All nodes and their attributes are already created
        path_iterator = 0
        # loop over all paths. Each path contains a list of segments
        for unified_path in self.paths:

            # define path section
            edge_iterator = 0
            for edge in unified_path.segments:
                cy_frag = "MERGE " + edge.to_cypher(skip_node_attrs=True, skip_node_labels=True) + " "
                cy_list.append(cy_frag)
                edge_iterator += 1

            # increase path iterator
            path_iterator += 1

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
                start_node = segment.start_node
                end_node = segment.end_node
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

                new_start_node = cutted_path[0].start_node
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
                n1: NodeItem = e.start_node
                n2: NodeItem = e.start_node
                n1.tidy_attrs(remove_None_values=False)
                n2.tidy_attrs(remove_None_values=False)
