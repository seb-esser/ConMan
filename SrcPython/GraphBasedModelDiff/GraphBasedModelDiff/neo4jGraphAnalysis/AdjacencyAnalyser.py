import numpy as np 
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.NodeItem import NodeItem
from neo4jGraphDiff.SetCalculator import SetCalculator


class AdjacencyAnalyser(object):
    """description of class"""

    def __init__(self, connector: Neo4jConnector):
        """

        @connector: neo4j database connector instance to perform queries
        """
        self.connector = connector


    def get_adjacency_matrix(self, label): 
        """
        calculates the adjacency matrix ordered by ascending hashsums
        @label: graph identifier, which the primary and connection nodes get queried from
        """
        # get all node ids of primary and connection nodes of one model
        cy_primary = Neo4jQueryFactory.get_primary_nodes(label)
        cy_con = Neo4jQueryFactory.get_connection_nodes(label)
        raw_response_primary = self.connector.run_cypher_statement(cy_primary)
        raw_response_con = self.connector.run_cypher_statement(cy_con)
        
        # cast results to NodeItem instances 
        nodes_primary = NodeItem.fromNeo4jResponseWouRel(raw_response_primary)
        nodes_con = NodeItem.fromNeo4jResponseWouRel(raw_response_con)
          
        # merge
        nodes = nodes_primary + nodes_con
        
        # get hashes of all nodes
        for n in nodes: 
            cy = Neo4jQueryFactory.get_hash_by_nodeId(label, n.id)
            raw_response = self.connector.run_cypher_statement(cy, 'hash')
            n.setHash(raw_response[0])

        # sort nodes by their hashsums      
        sorted_nodes = sorted(nodes, key=lambda nodeItem: nodeItem.hash)
        
        # build adjacency matrix
        calculator = SetCalculator()
        cartesian_prod = calculator.calc_cartesian_product(sorted_nodes, sorted_nodes)

        vals = []
        # query adjacency values
        for pair in cartesian_prod: 
            # check if rel exists
            cy = Neo4jQueryFactory.nodes_are_connected(pair[0].id, pair[1].id)
            # run cypher query
            raw_response = self.connector.run_cypher_statement(cy)
            # encode response
            con = raw_response[0]['are_connected']
            if con is True:
                vals.append(1)
            else: 
                vals.append(0)

        dims = len(sorted_nodes)
        adj_mtx = np.array(vals).reshape(dims,dims)
        print(adj_mtx)

        return adj_mtx 





