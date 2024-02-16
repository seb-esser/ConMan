from copy import deepcopy
from pprint import pprint
from typing import List
import re

import jsonpickle
import networkx

from neo4j_middleware import neo4jConnector
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
from neo4j_middleware.ResponseParser.GraphPath import GraphPath
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class GraphPattern:
    def __init__(self, paths=None):
        """
        graph pattern carries a pattern consisting of multiple segments
        @param paths:
        """
        if paths is None:
            self.paths: List[GraphPath] = []
        else:
            self.paths: List[GraphPath] = paths

    def __repr__(self):
        return 'GraphPattern instance composed by several GraphPath instances'

    @classmethod
    def from_neo4j_response(cls, raw):
        # decode cypher response
        raw_paths = raw

        if len(raw_paths) == 0:
            return None

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

    def get_last_node(self) -> NodeItem:
        """
        returns last node if pattern is a path
        """
        return self.paths[-1].get_last_node()

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

    def to_cypher_match(self, define_return: bool = False,
                        entType_guid_only: bool = False, skip_timestamps: bool = False,
                        optional_match: bool = False) -> str:
        """
        improved version to search for a specified graph pattern using a distinct node set definition
        @return:
        """

        if len(self.paths) == 0:
            # empty pattern
            return ''

        self.get_unified_edge_set()

        # init cypher query
        cy_list = []

        path_iterator = 0
        # loop over all paths. Each path contains a list of segments
        for path in self.paths:

            if optional_match:
                cy_list.append("OPTIONAL ")
            cy_list.append("MATCH ")
            cy_l = path.to_cypher(path_number=path_iterator, skip_timestamp=skip_timestamps
                                  , entType_guid_only=entType_guid_only)
            cy_list.extend(cy_l)

            # increase path iterator by one
            path_iterator += 1
            cy_list.append(' ')

        if define_return:
            num_paths = self.get_number_of_paths()

            return_cy = 'RETURN '
            for np in range(num_paths):
                return_cy += 'path{}, '.format(np)

            return_cy = return_cy[:-2]  # remove last ', '

            cy_list.append(return_cy)

        # build the final cypher statement
        cy_statement = ''.join(cy_list)

        return cy_statement

    def to_cypher_merge(self, nodes_specified=[], edges_specified=[]) -> str:
        """
        creates a cypher query string to create a given graph pattern in a target graph
         without recognizing existing items
        @return: cypher query statement as str
        """

        # init cypher query
        cy_list = []

        path_iterator = 0

        # list of nodes that observe which node was already defined in the query
        nodes_already_specified = []
        edges_already_specified = []

        if nodes_specified != []:
            nodes_already_specified.extend(nodes_specified)
        if edges_specified != []:
            edges_already_specified.extend(edges_specified)

        # loop over all paths. Each path contains a list of segments
        for unified_path in self.paths:

            # define path section
            edge_iterator = 0

            for edge in unified_path.segments:

                if edge.start_node not in nodes_already_specified:
                    skip_start_attrs = False
                    skip_start_labels = False
                else:
                    skip_start_attrs = True
                    skip_start_labels = True
                if edge.end_node not in nodes_already_specified:
                    skip_end_attrs = False
                    skip_end_labels = False
                else:
                    skip_end_attrs = True
                    skip_end_labels = True
                if edge in edges_already_specified and not edge.is_virtual_edge():
                    continue

                cy_frag = "MERGE " + edge.to_cypher(skip_start_node_attrs=skip_start_attrs,
                                                    skip_start_node_labels=skip_start_labels,
                                                    skip_end_node_attrs=skip_end_attrs,
                                                    skip_end_node_labels=skip_end_labels) + " "

                nodes_already_specified.append(edge.start_node)
                nodes_already_specified.append(edge.end_node)
                edges_already_specified.append(edge)

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
                start_node: NodeItem = segment.start_node
                end_node: NodeItem = segment.end_node

                if start_node.id == -1:
                    print("!")

                if start_node not in unified_pattern_node_list and start_node.id != -1:
                    unified_pattern_node_list.append(start_node)
                if end_node not in unified_pattern_node_list and end_node.id != -1:
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

        empty_paths = []
        # loop over all paths
        for path in self.paths:
            # a path consists of several segments (i.e., edges)
            initial_segments = list(path.segments)  # make deep copy
            for segment in initial_segments:

                # if segment.edge_id != -1:
                #     # this edge is a virtual one - skip
                #     continue

                if segment.edge_id in [e.edge_id for e in unified_segments] and segment.is_virtual_edge() is False:
                    # segment has been already tackled
                    # remove current segment from Path
                    path.remove_segments_by_id([segment.edge_id])
                else:
                    # segment appears the first time, therefore keep it and add it to the list
                    unified_segments.append(segment)

            if len(path.segments) == 0:
                empty_paths.append(path)

        # remove empty paths
        if len(empty_paths) > 0:
            new_list = []
            for v in self.paths:
                if v not in empty_paths:
                    new_list.append(v)
            self.paths = new_list

        return unified_segments

    def unify_edge_set(self) -> None:
        """
        unifies the edge set
        @return:
        """
        self.get_unified_edge_set()

        # in some situations, edges get removed such that a GraphPath with zero segments (i.e., edges) remains
        # remove those GraphPath instances from segments which have no egde anymore
        cleaned_paths = [p for p in self.paths if len(p.segments) != 0]

        self.paths = cleaned_paths

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
                n2: NodeItem = e.end_node
                n1.tidy_attrs(remove_None_values=False)
                n2.tidy_attrs(remove_None_values=False)

    def remove_highlight_labels(self):
        for p in self.paths:
            for e in p.segments:
                n1: NodeItem = e.start_node
                n2: NodeItem = e.end_node
                n1.labels.remove("ADDED")
                n1.labels.remove("DELETED")
                n1.labels.remove("MODIFIED")
                n2.labels.remove("ADDED")
                n2.labels.remove("DELETED")
                n2.labels.remove("MODIFIED")
                # ToDo Move this method into NodeItem

    def replace_timestamp(self, new_timestamp):
        """
        replaces the timestamp label in all nodes of the this graph pattern
        @param new_timestamp:
        @return:
        """

        old_timestamp = self.paths[0].get_start_node().get_timestamps()[0]

        for p in self.paths:
            for s in p.segments:
                n1: NodeItem = s.start_node
                n1.labels = [new_timestamp if item == old_timestamp else item for item in n1.labels]
                n2: NodeItem = s.end_node
                n2.labels = [new_timestamp if item == old_timestamp else item for item in n2.labels]

    def to_cypher_pattern_delete(self, nodes_specified, edges_specified) -> str:
        """
        removes a pattern. Prerequisite is that the pattern is entirely decoupled.
        @return: cypher statement
        """
        cy = self.to_cypher_match()
        num_paths = self.get_number_of_paths()
        if num_paths == 0:
            raise Exception("tried to delete a pattern but received zero path segments. ")

        cy += 'DETACH DELETE '
        for np in range(num_paths):
            cy += 'path{}, '.format(np)
        cy = cy[:-2]  # remove last ', '
        return cy
        #
        # # init cypher query
        # cy_list = []
        #
        # path_iterator = 0
        #
        # # list of nodes that observe which node was already defined in the query
        # nodes_already_specified = []
        # edges_already_specified = []
        #
        # if nodes_specified != []:
        #     nodes_already_specified.extend(nodes_specified)
        # if edges_specified != []:
        #     edges_already_specified.extend(edges_specified)
        #
        # # loop over all paths. Each path contains a list of segments
        # for unified_path in self.paths:
        #
        #     # define path section
        #     edge_iterator = 0
        #
        #     for edge in unified_path.segments:
        #
        #         if edge.start_node not in nodes_already_specified:
        #             skip_start_attrs = False
        #             skip_start_labels = False
        #         else:
        #             skip_start_attrs = True
        #             skip_start_labels = True
        #         if edge.end_node not in nodes_already_specified:
        #             skip_end_attrs = False
        #             skip_end_labels = False
        #         else:
        #             skip_end_attrs = True
        #             skip_end_labels = True
        #         if edge in edges_already_specified:
        #             continue
        #
        #         cy_frag = "DETACH DELETE " + edge.to_cypher(skip_start_node_attrs=skip_start_attrs,
        #                                             skip_start_node_labels=skip_start_labels,
        #                                             skip_end_node_attrs=skip_end_attrs,
        #                                             skip_end_node_labels=skip_end_labels) + " "
        #
        #         nodes_already_specified.append(edge.start_node)
        #         nodes_already_specified.append(edge.end_node)
        #         edges_already_specified.append(edge)
        #
        #         cy_list.append(cy_frag)
        #         edge_iterator += 1
        #
        #     # increase path iterator
        #     path_iterator += 1
        #
        # cy_statement = ''.join(cy_list)
        #
        # return cy_statement

    def to_cypher_node_delete(self, include_detach=False, ignore_nodes=[]):
        """
        method assumes that all nodes have been already specified by a match function

        @return:
        """

        pattern_nodes = self.get_unified_node_set()

        nodes_to_be_removed = [x for x in pattern_nodes if x not in ignore_nodes]

        cy = ""

        for node in nodes_to_be_removed:
            if include_detach:
                cy += "DETACH "
            cy += "DELETE {} ".format(node.to_cypher(skip_labels=True, skip_attributes=True))

        return cy

    def is_empty(self):
        if self.get_number_of_paths() == 0:
            return True
        else:
            return False

    def remove_OwnerHistory_links(self):
        """

        @return:
        """
        # ToDo: remove?
        for p in self.paths:
            for seg in p.segments:
                if seg.get_rel_type() == "OwnerHistory":
                    self.paths.remove(p)

    def to_nx_graph(self, cluster_type=None, node_highlighter: str = "") -> networkx.DiGraph:
        """

        @param node_highlighter:
        @param cluster_type:
        @return:
        """
        graph = networkx.DiGraph()

        nodes = self.get_unified_node_set()

        for node in nodes:
            graph.add_node(node.get_node_identifier())
            networkx.set_node_attributes(graph, {node.get_node_identifier(): node.attrs})
            networkx.set_node_attributes(graph, {node.get_node_identifier(): {"NodeType": node.get_node_type(),
                                                                              "Highlighter": node_highlighter}})

        for edge in self.get_unified_edge_set():

            if edge.is_virtual_edge():
                continue

            graph.add_edge(u_of_edge=edge.start_node.get_node_identifier(),
                           v_of_edge=edge.end_node.get_node_identifier())
            networkx.set_edge_attributes(graph,
                                         {
                                             (edge.start_node.get_node_identifier(),
                                              edge.end_node.get_node_identifier()): {
                                                 "relType": edge.attributes["rel_type"],
                                                 "clusterType": cluster_type
                                             }
                                         })
        return graph

    def to_arrows_visualization(self, ignore_null_values: bool = False, create_relaxed_pattern: bool = False):
        """
        creates a json that can be used for arrows.app visualization
        :param ignore_null_values: skip attr values with None/null
        :param create_relaxed_pattern: skip attributes that are not relevant to create unique match
        """

        # load base
        with open("neo4j_middleware/base_arrows_format.json") as f:
            content = f.read()
        arrows = jsonpickle.decode(content)

        x_pos = 0
        y_pos = 0

        nodes = self.get_unified_node_set()

        for node in nodes:
            # create arrows fragment
            arrows_node = node.to_arrows_vis(ignore_null_values=ignore_null_values,
                                             x_pos=x_pos,
                                             y_pos=y_pos,
                                             create_relaxed_pattern = create_relaxed_pattern)
            arrows["nodes"].append(arrows_node)
            x_pos += 100

        edges = self.get_unified_edge_set()

        for edge in edges:
            # skip virtual edges
            if edge.edge_id == -1:
                continue

            # create arrows fragment
            arrows_edge = edge.to_arrows_vis()
            arrows["relationships"].append(arrows_edge)

        return arrows
