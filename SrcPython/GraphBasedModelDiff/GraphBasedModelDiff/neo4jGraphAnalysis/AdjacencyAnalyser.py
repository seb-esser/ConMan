import numpy as np 
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.NodeItem import NodeItem

class AdjacencyAnalyser(object):
    """description of class"""

    def __init__(self, connector: Neo4jConnector):
        """

        @connector: neo4j database connector instance to perform queries
        """
        self.connector = connector


    def get_adjacency_matrix(self, label): 

        # get all node ids of primary and connection nodes of one model
        cy = Neo4jQueryFactory.get_primary_nodes(label)
        raw_response = self.connector.run_cypher_statement(cy)
        nodes = NodeItem.fromNeo4jResponseWouRel(raw_response)
               
        # get hashes of all nodes
        for n in nodes: 
            cy = Neo4jQueryFactory.get_hash_by_nodeId(label, n.id)
            raw_response = self.connector.run_cypher_statement(cy, 'hash')
            n.setHash(raw_response[0])


        # sort nodes by their hashsums
        print('nodes in unsorted order: ')
        for n in nodes: 
            print(n.hash)

        print('\nnodes in sorted order: ')
        sorted_nodes = sorted(nodes, key=lambda nodeItem: nodeItem.hash)
        for n in sorted_nodes: 
            print(n.hash)

        # build adjacency matrix
        a = 1






