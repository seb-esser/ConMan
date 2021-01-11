
import abc

from .DiffUtilities import DiffUtilities
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory
from neo4j_middleware.ChildData import ChildData
from neo4j_middleware.NodeDiffData import NodeDiffData


class DirectedSubgraphDiff(abc.ABC):
    """description of class"""

    @abc.abstractmethod
    def __init__(self, connector, label_init, label_updated, diffIgnorePath = None): 

        if diffIgnorePath != None:
            self.utils = DiffUtilities(diffIgnorePath)
            self.UseDiffIgnore = True
        else: 
            self.UseDiffIgnore = False

        self.connector = connector
        self.label_init = label_init
        self.label_updated = label_updated
        

    # abstract definition of diffSubgraphs() method, implemented in HashDiff and CompareDiff classes
    @abc.abstractclassmethod
    def diffSubgraphs(self, nodeId_init, nodeId_updated):
        pass

    # common method for all subclasses
    def __getChildren(self, label, parentNodeId, indent = 0): 

        # queries all directed neighbors, their relType and their node hashes

        match = 'MATCH (n:{}) -[r]->(c)'.format(label)
        where = 'WHERE ID(n) = {}'.format(parentNodeId)
        ret = 'RETURN ID(c), type(r), c.entityType'

        cypher = neo4jUtils.BuildMultiStatement([match, where, ret])

        res_raw = self.connector.run_cypher_statement(cypher)

        res = self.__unpackChildren(res_raw)

       
        # check if leave node got touched
        if len(res) == 0:            
            return []
        else:
            return res


# -- Helper Functions --- 
    def __unpackChildren(self, result): 
        ret_val = []
        for res in result: 
            child = ChildData(res[0], res[1], res[2]) 
            ret_val.append(child)
        return ret_val



