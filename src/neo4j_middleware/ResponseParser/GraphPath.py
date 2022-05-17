from typing import List

from neo4j_middleware.CypherUtilities import CypherUtilities
from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.Neo4jFactory import Neo4jFactory


class GraphPath:

    def __init__(self, segments: List[EdgeItem]):
        self.segments = segments

    def get_start_node(self) -> NodeItem:
        """
        returns the first node of the path
        @return:
        """
        return self.segments[0].start_node

    def get_last_node(self) -> NodeItem:
        """
        returns the last node of the path
        @return:
        """
        return self.segments[-1].end_node

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

    def to_cypher(self, path_number: int = None):
        """
        serializes the GraphPath object into a string representation
        @param path_number: specify an integer indicating the path number inside a pattern, otherwise None
        @return: cypher string fragment
        """

        # init local vars of this method
        cy = ''
        cy_list = []

        # init match-statement
        cy = 'path{} ='.format(path_number, self.segments[0].start_node.to_cypher())
        cy_list.append(cy)

        last_end_node: NodeItem

        # loop over all segments of the current path and append them to the call
        for segment in self.segments:
            try:
                if segment.start_node == last_end_node:
                    # # remove last comma
                    # cy_list[-1] = cy_list[-1][:-2]
                    # ToDo: sometimes not the last comma but the closing brackets are cutted away

                    # append edge without specifying the start node again
                    skip_start = True
                    cy = segment.to_cypher(skip_start_node=skip_start, skip_end_node_attrs=True)
                else:
                    cy = segment.to_cypher(skip_start_node=False, skip_start_node_attrs=False, skip_end_node_attrs=True)
                    # cy += ', '
            except:

                cy = segment.to_cypher(skip_start_node=False, skip_start_node_attrs=False, skip_end_node_attrs=True)
                # cy += ', '
            cy_list.append(cy)

            # update last_end_node attribute
            last_end_node = segment.end_node

        return ' '.join(cy_list)

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


