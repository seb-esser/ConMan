from typing import List

from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.Neo4jFactory import Neo4jFactory


class GraphPath:

    def __init__(self, segments: List[EdgeItem]):
        self.segments = segments

    def get_start_node(self) -> NodeItem:
        return self.segments[0].startNode

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

        nodes = NodeItem.from_neo4j_response(raw_nodes)
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
        @return: cypher string fragment
        """

        # init local vars of this method
        cy = ''
        seg_number = 1
        cy_list = []

        if entry_node_identifier is not None:
            start_node = entry_node_identifier
        else:
            start_node = self.segments[0].startNode.get_entity_type()

        # init cypher statement
        if path_number is not None:
            cy = 'MATCH path{} = ({})'.format(path_number, start_node)
        else:
            cy = 'MATCH ({})'.format(seg_number, start_node)

        cy_list.append(cy)

        # loop over all segments of the current path
        for segment in self.segments:
            end_node_type: str = segment.endNode.get_entity_type()
            end_node_attrs: dict = {k: v for k, v in segment.endNode.attrs.items() if v is not None}

            end_node_attrs.pop('p21_id', None)

            rel_attrs = segment.attributes

            cy = '-[r{0}{1} {2} ]->({3}{0} {4} )'\
                .format(seg_number,
                        path_number,
                        Neo4jFactory.formatDict(rel_attrs),
                        node_var,
                        Neo4jFactory.formatDict(end_node_attrs)
                        # end_node_type

                        )
            seg_number += 1
            cy_list.append(cy)
        return cy_list

    def remove_segments_by_id(self, segment_ids):
        """
        removes an edge from the segments list of this GraphPath instance
        @param segment_ids:
        @return:
        """
        for seg_id in segment_ids:
            # find corresponding edgeItem instance in list
            edge = next((x for x in self.segments if x.edge_id == seg_id), None)
            if edge is not None:
                # remove the segment
                self.segments.remove(edge)
            else:
                raise Exception('could not find edgeItem in segments of current path. ')

    def get_entry_node(self) -> NodeItem:
        """
        returns the first node of the path
        @return:
        """
        return self.segments[0].startNode
