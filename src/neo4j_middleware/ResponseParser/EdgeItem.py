from typing import Dict
import re

from neo4j_middleware.CypherUtilities import CypherUtilities
from neo4j_middleware.ResponseParser import NodeItem
from neo4j_middleware.Neo4jFactory import Neo4jFactory


class EdgeItem:
    def __init__(self, start_node: NodeItem, end_node: NodeItem, rel_id: int):
        self.start_node: NodeItem = start_node
        self.end_node: NodeItem = end_node
        self.edge_id: int = rel_id
        self.attributes: dict = {}
        self.labels = []
        self.edge_identifier = ""
        self.is_undirected = False

    def __repr__(self):
        return 'EdgeItem: id: {} var: {} fromNode: {} toNode {} attrs: {} labels: {}' \
            .format(
            self.edge_id, self.edge_identifier, self.start_node.id, self.end_node.id, self.attributes, self.labels)

    def __eq__(self, other):
        """
        compares two edges and returns true if both edges are considered as equal
        @param other:
        @return:
        """

        # start_equal = self.start_node == other.start_node
        # end_equal = self.end_node == other.end_node
        # rel_attrs_equal = self.attributes == other.attributes
        id_equal = self.edge_id == other.edge_id
        # if all([start_equal, end_equal, rel_attrs_equal]):
        return id_equal

    @classmethod
    def from_neo4j_response(cls, raw: str, nodes):
        """
        returns a list of EdgeItem instances from a given neo4j response string
        @raw: the neo4j response
        @nodes: a list of nodeItem instances
        @return: a list of EdgeItem instances in a list
        """

        edges = []

        for edge in raw:
            raw_startnode_id = edge.start_node.id
            raw_endnode_id = edge.end_node.id
            edge_id = edge.id

            start_node = next(x for x in nodes if x.id == raw_startnode_id)
            end_node = next(x for x in nodes if x.id == raw_endnode_id)

            e = cls(start_node, end_node, edge_id)
            edges.append(e)

        return edges

    @classmethod
    def from_cypher_fragment(cls, raw_edge, node_left: NodeItem, node_right: NodeItem):

        edge_semantics = raw_edge[1]
        # pre-processing
        if edge_semantics[-1] != "}":
            edge_semantics += "{}"

        reg_attr_extractor = r"\{([^]]+)\}"
        reg_attr_separator = r"(.+?):(.+?),"
        reg_node_labels = r":([^]]+)\{"
        reg_edge_var = r"^(.+?)(:|^)"

        # get edge var
        try:
            edge_var = re.findall(reg_edge_var, edge_semantics)[0][0]
        except:
            edge_var = ""

        # get edge labels
        labels = []
        node_label_raw = re.findall(reg_node_labels, edge_semantics)
        if len(node_label_raw) != 0:
            labels = node_label_raw[0].replace(" ", "").split(":")
        else:
            raise Exception("Error when parsing edges from cypher statement. Each edge must have at least one label. ")

        # get attributes
        attributes = ""
        attributes_raw = re.findall(reg_attr_extractor, edge_semantics)
        if len(attributes_raw) != 0:
            attributes = attributes_raw[0] + ", "

        # get attributes with regex
        all_attributes_raw = re.findall(reg_attr_separator, attributes)
        # cast attributes to python dict
        attr_dict = CypherUtilities.parse_attrs(all_attributes_raw)

        # instantiate a new edge item
        if raw_edge[0] == "<":
            edge = cls(start_node=node_right, end_node=node_left, rel_id=0)
        else:
            edge = cls(start_node=node_left, end_node=node_right, rel_id=0)

        # assign extracted semantics
        edge.labels = labels
        edge.attributes = attr_dict
        edge.edge_identifier = edge_var

        if len(raw_edge[0]) == 0 and len(raw_edge[2]) == 0:
            edge.is_undirected = True

        return edge

    def set_attributes(self, attrs: Dict):
        """
        sets the attribute property
        @param attrs: queried dictionary from neo4j graph
        @return: Nothing
        """
        self.attributes = attrs

    def to_cypher(self,
                  skip_start_node=False,
                  skip_end_node=False,
                  skip_node_attrs=False,
                  skip_node_labels=False,
                  skip_edge_attrs=False) -> str:
        """
        returns a cypher statement to search for this edge item.
        @return: cypher statement as str
        """

        # pre-define components of query

        cy_start_node = ""
        cy_edge_identifier = ""
        cy_edge_labels = ""
        cy_edge_attributes = ""
        cy_directed = ""
        cy_end_node = ""

        # parse nodes
        if skip_start_node is False:
            cy_start_node = self.start_node.to_cypher(
                skip_attributes=skip_node_attrs, skip_labels=skip_node_labels)
        if skip_end_node is False:
            cy_end_node = self.end_node.to_cypher(
                skip_attributes=skip_node_attrs, skip_labels=skip_node_labels)

        # parse edge attributes, labels and identifiers
        cy_edge_identifier = self.edge_identifier

        if self.attributes != {}:
            if skip_edge_attrs is False:
                cy_edge_attributes = Neo4jFactory.formatDict(self.attributes)

        if len(self.labels) > 0:
            for label in self.labels:
                cy_edge_labels += ":{}".format(label)

        # parse direction
        if self.is_undirected is False:
            cy_directed = ">"

        # construct statement
        cy = '{}-[{}{}{}]-{}{}'.format(
            cy_start_node,
            cy_edge_identifier,
            cy_edge_labels,
            cy_edge_attributes,
            cy_directed,
            cy_end_node
                )

        return cy

# def to_cypher_fragment(self, target_identifier: str, segment_identifier: int, relationship_iterator: int) -> str:
#     """
#     returns a fragment of a cypher statement to assemble several edges to a path
#     @param target_identifier:
#     @param segment_identifier:
#     @param relationship_iterator:
#     @return: cypher fragment as str
#     """
#     cy = '-[r{3}{2}{0}]->{1}'.format(
#         Neo4jFactory.formatDict(self.attributes),
#         self.end_node.to_cypher(timestamp=None, node_identifier=target_identifier),
#         relationship_iterator, segment_identifier)
#     return cy

# def to_cypher_create(self, target_identifier: str, segment_identifier: int, relationship_iterator: int):
#     """
#     returns a cypher command to create the edge. the edge is labeled with 'rel'
#     @return: cypher statement as str
#     """
#
#     edge_labels = ""
#     if len(self.labels) == 0:
#         edge_labels = ""
#         # ToDo: catch case when no label is provided but attributes are around
#     else:
#         for label in self.labels:
#             edge_labels += "{}".format(label)
#
#     if self.is_undirected:
#
#         cy = '-[r{3}{2}:{4}{0}]-({1})'.format(
#             Neo4jFactory.formatDict(self.attributes),
#             target_identifier,
#             relationship_iterator,
#             segment_identifier,
#             edge_labels)
#     else:
#         cy = '-[r{3}{2}:{4}{0}]->({1})'.format(
#             Neo4jFactory.formatDict(self.attributes),
#             target_identifier,
#             relationship_iterator,
#             segment_identifier,
#             edge_labels)
#
#     return cy

# def to_cypher_individual_merge(self, target_timestamp: str, segment_identifier: int, relationship_iterator: int):
#     cy1 = 'MERGE {}'.format(
#         self.start_node.to_cypher(
#             node_identifier='a', include_nodeType_label=True, timestamp=target_timestamp)
#     )
#     cy2 = 'MERGE {}'.format(
#         self.end_node.to_cypher(
#             node_identifier='b', include_nodeType_label=True, timestamp=target_timestamp)
#     )
#     cy3 = 'MERGE (a)-[r{0}{1}:rel{2}]->(b)'.format(
#         segment_identifier, relationship_iterator, Neo4jFactory.formatDict(self.attributes))
#
#     return Neo4jFactory.BuildMultiStatement([cy1, cy2, cy3])
