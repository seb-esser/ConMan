import abc

from .DiffUtilities import DiffUtilities
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory

# classes to decode neo4j query responses
from neo4j_middleware.NodeData import NodeData
from neo4j_middleware.NodeDiffData import NodeDiffData


class DirectedSubgraphDiff(abc.ABC):
    """abstract super class for all subgraph diff methods """

    @abc.abstractmethod
    def __init__(self, connector, label_init, label_updated, diffIgnorePath=None, toConsole=False):

        self.toConsole = toConsole

        if diffIgnorePath != None:
            self.utils = DiffUtilities(diffIgnorePath)
            self.UseDiffIgnore = True
        else:
            self.UseDiffIgnore = False

        self.connector = connector
        self.label_init = label_init
        self.label_updated = label_updated

    # abstract definition of diffSubgraphs() method, implemented in HashDiff and CompareDiff classes
    @abc.abstractmethod
    def diffSubgraphs(self, nodeId_init, nodeId_updated):
        pass

    # common method for all subclasses
    def __getChildren(self, label, parent_node_id, indent=0):

        # queries all directed children, their relType and their node hashes

        cypher = neo4jQueryFactory.GetChildNodesByParentNodeId(label, parent_node_id)
        raw = self.connector.run_cypher_statement(cypher)

        # unpack neo4j response into a list if NodeData instances
        res = NodeData.fromNeo4jResponseWithRel(raw)

        # check if leave node got touched
        if len(res) == 0:
            return []
        else:
            return res

    def __applyDiffIgnore_Nodes(self, node_list):
        """ removes nodes from a list if their type is set to be ignored """
        if self.UseDiffIgnore == False:
            raise Exception(
                'UseDiffIgnore was set to false. You have tried to apply it anyway. Please check your settings')

        # ToDo: Logging: Add info statement that ingoreNodes got applied. 

        # get entity types that shall be ignored in the subgraph diff
        ignore_entityTypes = self.utils.diffIngore.ignore_node_tpes

        return_list = node_list

        for node in node_list:
            if node.entityType in ignore_entityTypes:
                return_list.remove(node)

        # ToDo: Logging: Add info statement if nodes got removed or not
        return return_list

    def __getNodeDataByNodeId(self, nodeId): 
        cypher = neo4jQueryFactory.GetNodeDataById(nodeId)
        raw = self.connector.run_cypher_statement(cypher)

        # unpack neo4j response into a list if NodeData instances
        res = NodeData.fromNeo4jResponseWouRel(raw)
        return res