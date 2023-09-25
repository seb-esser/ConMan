from pprint import pprint

import networkx

from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class Neo2NxConnector:

    def __init__(self, connector: Neo4jConnector):
        self.connector = connector

    def translate_neo2nx(self, timestamp: str):
        """
        takes a given neo4j graph and parses it into a networkX DiGraph representation
        @return:
        """
        nx_graph = networkx.DiGraph()

        # get all nodes forming an IFC model
        cy = Neo4jQueryFactory.get_all_nodes(timestamp)
        raw = self.connector.run_cypher_statement(cy)

        neo_nodes = NodeItem.from_neo4j_response(raw)

        # translate nodes into nx graph
        for neo_node in neo_nodes:
            nx_graph.add_node(neo_node.get_node_identifier())

            # set node attributes
            networkx.set_node_attributes(nx_graph, {neo_node.get_node_identifier(): neo_node.attrs})
            networkx.set_node_attributes(nx_graph,
                                         {neo_node.get_node_identifier(): {"NodeType": neo_node.get_node_type()}
                                          })

        # get all edges
        cy = Neo4jQueryFactory.get_all_edge_patterns(timestamp)
        raw = self.connector.run_cypher_statement(cy)

        pattern = GraphPattern.from_neo4j_response(raw)

        for path in pattern.paths:
            edge = path.segments[0]

            nx_graph.add_edge(u_of_edge=edge.start_node.get_node_identifier(),
                              v_of_edge=edge.end_node.get_node_identifier())
            networkx.set_edge_attributes(nx_graph,
                                         {
                                             (edge.start_node.get_node_identifier(),
                                              edge.end_node.get_node_identifier()): {
                                                 "relType": edge.attributes["rel_type"]
                                             }
                                         })

        # return nx graph
        return nx_graph
