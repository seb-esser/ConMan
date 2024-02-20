import re
from typing import List

from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class GraphPath:

    def __init__(self, segments: List[EdgeItem]):
        self.segments: List[EdgeItem] = segments

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
        if len(self.segments) > 1:
            return self.segments[-1].end_node
        else:
            return self.segments[0].start_node

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

        if len(segments) == 0:
            raise Exception("Graph Path got instantiated but no segments have been unpacked. ")

        return cls(segments)

    def __repr__(self):
        return 'GraphPath instance. No segments: {}'.format(len(self.segments))

    def to_cypher(self, path_number: int = None, skip_timestamp=False, entType_guid_only: bool=False):
        """
        serializes the GraphPath object into a string representation
        @param entType_guid_only: use reduced node attribute representation. should be False for most cases
        @param path_number: specify an integer indicating the path number inside a pattern, otherwise None
        @param skip_timestamp: remove timestamps from nodes
        @return: cypher string fragment
        """

        # init local vars of this method

        cy_list = []

        # init match-statement
        cy = 'path{} ='.format(path_number, self.segments[0].start_node.to_cypher(entType_guid_only=entType_guid_only))
        cy_list.append(cy)

        last_end_node: NodeItem

        # loop over all segments of the current path and append them to the call
        for segment in self.segments:
            if segment.is_virtual_edge():
                cy = segment.to_cypher(entType_guid_only=entType_guid_only)
                cy_list.append(cy)
                continue

            try:
                if segment.start_node == last_end_node:
                    # # remove last comma
                    # cy_list[-1] = cy_list[-1][:-2]
                    # ToDo: sometimes not the last comma but the closing brackets are cutted away

                    # append edge without specifying the start node again
                    skip_start = True
                    cy = segment.to_cypher(skip_start_node=skip_start, entType_guid_only=True)
                else:
                    cy = segment.to_cypher(skip_start_node=False, entType_guid_only=True)
                    # cy += ', '
            except:

                cy = segment.to_cypher(skip_start_node=False, entType_guid_only=True)
                # cy += ', '
            cy_list.append(cy)

            # update last_end_node attribute
            last_end_node = segment.end_node

        cy = ' '.join(cy_list)

        if skip_timestamp:
            cy = re.sub(r".ts[a-zA-Z0-9]{15}", r"", cy)

        return cy

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

    def tidy_node_attributes(self):
        for segment in self.segments:
            segment.start_node.tidy_attrs()
            segment.end_node.tidy_attrs()

