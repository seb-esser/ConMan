from .Neo4jFactory import Neo4jFactory


class Neo4jQueryFactory(Neo4jFactory):
    """ provides a set of methods to create cypher strings querying the neo4j database"""
    def __init__(self):
        pass

    @classmethod
    def diff_nodes(cls, node_id_left: int, node_id_right: int) -> str:
        """Calculates the attribute diff between two nodes and returns a cypher string.
        !! APOC library needs to be installed in the database instance !!

        Parameters
        ----------
        node_id_left : left node to be compared
        node_id_right: right node to be compared

        Returns
        -------
        cypher string to be executed using a connector instance.

        """
        query_left = 'MATCH (l) WHERE ID(l) = {}'.format(node_id_left)
        query_right = 'MATCH (r) WHERE ID(r) = {}'.format(node_id_right)
        ret_statement = 'RETURN apoc.diff.nodes(l,r)'
        return Neo4jFactory.BuildMultiStatement([query_left, query_right, ret_statement])

    @classmethod
    def get_nodeId_byP21(cls, p21_id: int, label: str = None):
        """ returns a cypher statement to query a node by its P21_id and a given (optional) label. """

        if label is not None:
            query = 'MATCH (n:{})'.format(label)
        else:
            query = 'MATCH (n)'

        wh = 'WHERE n.p21_id = {}'.format(p21_id)
        ret_statement = 'RETURN ID(n)'
        return Neo4jFactory.BuildMultiStatement([query, wh, ret_statement])

    @classmethod
    def get_primary_nodes(cls, label: str) -> str:
        """
        Queries all primary nodes, which have the given label attached.
        @param label:
        @return: cypher query string
        """
        match = 'MATCH (n:PrimaryNode:{}) '.format(label)
        ret_statement = 'RETURN ID(n), n.entityType'
        return Neo4jFactory.BuildMultiStatement([match, ret_statement])

    @classmethod
    def get_connection_nodes(cls, label: str) -> str: 
        """
        Queries all primary nodes, which have the given label attached.
        @param label:
        @return: cypher query string
        """
        match = 'MATCH (n:ConnectionNode:{}) '.format(label)
        ret_statement = 'RETURN ID(n), n.entityType'
        return Neo4jFactory.BuildMultiStatement([match, ret_statement])

    @classmethod
    def get_hash_by_nodeId(cls, label: str, nodeId: int, attrIgnoreList=None) -> str:
        """
        Calculates the hash sum over a given node. Use attrIgnoreList to specify attribute names that should be excluded when calculating the hash
        @param label: model label
        @param nodeId: the node ID
        @param attrIgnoreList: attributes to be ignored in the hash calculation
        @return: cypher query string
        """

        getModel = 'MATCH(n:{})'.format(label)
        where = 'WHERE ID(n) = {}'.format(nodeId)

        open_sub = 'CALL {WITH n'

        removeLabel = 'REMOVE n:{}'.format(label)

        # apply diffIgnore attributes if staged
        if attrIgnoreList == None:
            calc_fingerprint = 'with apoc.hashing.fingerprint(n) as hash RETURN hash'
        else:
            # open
            ignore_str = '['

            # all attrs
            for attr in attrIgnoreList:
                ignore_str = ignore_str + '"{}", '.format(attr)

            # remove last comma
            ignore_str = ignore_str[:-2]
            # close
            ignore_str = ignore_str + ']'

            calc_fingerprint = 'with apoc.hashing.fingerprint(n, {}) as hash RETURN hash'.format(ignore_str)

        close_sub = '}'
        add_label_again = 'SET n:{}'.format(label)
        return_results = 'RETURN hash'
        return Neo4jFactory.BuildMultiStatement([getModel, where, open_sub, removeLabel, calc_fingerprint, close_sub, add_label_again, return_results])


    @classmethod
    def get_child_nodes(cls, label: str, parent_node_id: int) -> str:
        """
        search for all nodes that have an incoming edge from the specified parent node and carries the similar label
        @param label: model identifier
        @param parent_node_id: the node id of the parent node
        @return: cypher query string
        """
        match = 'MATCH (n:{}) -[r]->(c)'.format(label)
        where = 'WHERE ID(n) = {}'.format(parent_node_id)
        ret = 'RETURN ID(c), type(r), c.entityType'
        return Neo4jFactory.BuildMultiStatement([match, where, ret])

    @classmethod
    def get_node_data_by_id(cls, nodeId: int) -> str:
        """
        Query the ID and the entityType attribute
        @param nodeId: the node id in the neo4j database
        @return: cypher query string
        """
        match = 'MATCH (n)'
        where = 'WHERE ID(n) = {}'.format(nodeId)
        ret = 'RETURN ID(n), n.entityType'
        return Neo4jFactory.BuildMultiStatement([match, where, ret])

    @classmethod
    def get_node_properties_by_id(cls, nodeId: int) -> str:
        """
        Query all params of a node specified by its node id
        @param nodeId: the node id in the neo4j database
        @return: cypher query string
        """
        match = 'MATCH (n)'
        where = 'WHERE ID(n) = {}'.format(nodeId)
        ret = 'RETURN properties(n)'
        return Neo4jFactory.BuildMultiStatement([match, where, ret])

    @classmethod
    def nodes_are_connected(cls, node_id_a: int, node_id_b: int) -> str:
        """
        checks if two given nodes have a directed edge from a to b
        @param node_id_a: node a 
        @param node_id_b: node b
        @return: cypher query string
        """
        match_a = 'MATCH (n) WHERE ID(n) = {}'.format(node_id_a)
        match_b = 'MATCH (m) WHERE ID(m) = {}'.format(node_id_b)
        ret = 'RETURN exists((n)-[]->(m)) as are_connected'
        return Neo4jFactory.BuildMultiStatement([match_a, match_b, ret])

# ticket_PostEvent-VerifyParsedModel
# -- create a new method GetNumberOfNodesInGraph(cls, label) here --
