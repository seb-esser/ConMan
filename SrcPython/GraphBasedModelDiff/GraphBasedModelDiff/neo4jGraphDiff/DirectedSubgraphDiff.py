import abc

from neo4jGraphDiff.SetCalculator import SetCalculator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.NodeItem import NodeItem


class DirectedSubgraphDiff(abc.ABC):
    """abstract super class for all subgraph diff methods """

    @abc.abstractmethod
    def __init__(self, connector, label_init, label_updated, configuration):

        # config contains basic settings about logging and console behavior
        self.configuration = configuration

        # utils provides methods to compare two sets of nodes based on specified criteria
        self.utils = SetCalculator()

        # the connector is used to perform cypher queries on the neo4j database
        self.connector = connector

        # labels to identify two graphs resp models
        self.label_init = label_init
        self.label_updated = label_updated

    def toConsole(self):
        """ helper method to trigger printToConsole """
        if self.configuration.LogSettings.logToConsole:
            return True
        else:
            return False

    # abstract definition of diffSubgraphs() method, implemented in HashDiff and CompareDiff classes
    @abc.abstractmethod
    def diff_subgraphs(self, node_init, node_updated):
        """

        @param node_init: start node for DFS initial graph
        @param node_updated: start node for DFS updated graph
        """
        pass

    # common method for all subclasses
    def get_children_nodes(self, label: str, parent_node_id: int, indent: int = 0) -> list:
        """
        Query a list of all direct child nodes to the given parent node
        @param label: the model label
        @param parent_node_id:
        @param indent:
        @return:
        """
        # queries all directed children, their relType and their node hashes

        cypher = Neo4jQueryFactory.get_child_nodes(label, parent_node_id)
        raw = self.connector.run_cypher_statement(cypher)

        # unpack neo4j response into a list if NodeItem instances
        res = NodeItem.fromNeo4jResponseWithRel(raw)

        # check if leave node got touched
        if len(res) == 0:
            return []
        else:
            return res

    def __applyDiffIgnore_Nodes(self, node_list):
        """ removes nodes from a list if their type is set to be ignored """

        # ToDo: Logging: Add info statement that ingoreNodes got applied. 

        # get entity types that shall be ignored in the subgraph diff
        ignore_entityTypes = self.configuration.DiffSettings.diffIgnoreEntityTypes  # list of strings

        # stop here if no entityTypes should be ignored
        if len(ignore_entityTypes) == 0:
            return node_list

        return_list = node_list

        for node in node_list:
            if node.entityType in ignore_entityTypes:
                return_list.remove(node)

        # ToDo: Logging: Add info statement if nodes got removed or not
        return return_list

    def __get_node_data_by_id(self, nodeId: int):
        """
        executes a cypher query to get some node data
        @param nodeId:
        @return:
        """
        cypher = Neo4jQueryFactory.get_node_data_by_id(nodeId)
        raw = self.connector.run_cypher_statement(cypher)

        # unpack neo4j response into a list if NodeItem instances
        res = NodeItem.fromNeo4jResponseWouRel(raw)
        return res
