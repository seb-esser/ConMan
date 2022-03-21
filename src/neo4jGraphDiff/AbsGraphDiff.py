import abc

from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.SetCalculator import SetCalculator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeDiffData import NodeDiffData
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class AbsGraphDiff(abc.ABC):
    """abstract super class for all subgraph diff methods """

    @abc.abstractmethod
    def __init__(self, connector, label_init, label_updated, configuration):

        # config contains basic settings about logging and console behavior
        self.configuration: Configuration = configuration

        # utils provides methods to compare two sets of nodes based on specified criteria
        self.utils = SetCalculator()

        # the connector is used to perform cypher queries on the neo4j database
        self.connector: Neo4jConnector = connector

        # labels to identify two graphs resp models
        self.label_init: str = label_init
        self.label_updated: str = label_updated

    def toConsole(self):
        """ helper method to trigger printToConsole """
        if self.configuration.LogSettings.logToConsole:
            return True
        else:
            return False

    # common method for all subclasses
    def get_children_nodes(self, label: str, parent_node_id: int) -> list:
        """
        Query a list of all direct child nodes to the given parent node
        @param label: the model label
        @param parent_node_id:
        @param indent:
        @return:
        """

        # queries all directed children, their rel_type and their node hashes
        cypher = Neo4jQueryFactory.get_child_nodes(label, parent_node_id)
        raw = self.connector.run_cypher_statement(cypher)

        # unpack neo4j response into a list if NodeItem instances
        res = NodeItem.fromNeo4jResponseWithRel(raw)

        # check if leave node got touched
        if len(res) == 0:
            return []
        else:
            return res

    def apply_diff_ignore_nodes(self, node_list):
        """ removes nodes from a list if their type is set to be ignored """

        # ToDo: Logging: Add info statement that ignoreNodes got applied.

        # get primary_node_type types that shall be ignored in the subgraph diff
        ignore_entityTypes = self.configuration.DiffSettings.diffIgnoreEntityTypes  # list of strings

        # stop here if no entityTypes should be ignored
        if len(ignore_entityTypes) == 0:
            return node_list

        return_list = node_list

        for node in node_list:
            if node.entity_type in ignore_entityTypes:
                return_list.remove(node)

        # ToDo: Logging: Add info statement if nodes got removed or not
        return return_list

    def apply_diff_ignore_attributes(self, diff: NodeDiffData) -> NodeDiffData:
        """
        removes attributes from a dictionary that were stated to be ignored
        @param diff: the diff object
        @return: a cleared diff
        """
        ignore_attrs = self.configuration.DiffSettings.diffIgnoreAttrs
        for ignore in ignore_attrs:
            if ignore in diff.AttrsUnchanged:
                del diff.AttrsUnchanged[ignore]
            if ignore in diff.AttrsAdded:
                del diff.AttrsAdded[ignore]
            if ignore in diff.AttrsDeleted:
                del diff.AttrsDeleted[ignore]
            if ignore in diff.AttrsModified:
                del diff.AttrsModified[ignore]

        return diff

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
