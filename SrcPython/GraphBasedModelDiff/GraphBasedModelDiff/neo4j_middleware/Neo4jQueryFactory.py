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
        ret_statement = 'RETURN ID(n), n.EntityType, PROPERTIES(n)'
        return Neo4jFactory.BuildMultiStatement([match, ret_statement])

    @classmethod
    def get_connection_nodes(cls, label: str) -> str: 
        """
        Queries all primary nodes, which have the given label attached.
        @param label:
        @return: cypher query string
        """
        match = 'MATCH (n:ConnectionNode:{}) '.format(label)
        ret_statement = 'RETURN ID(n), n.EntityType, PROPERTIES(n)'
        return Neo4jFactory.BuildMultiStatement([match, ret_statement])

    @classmethod
    def get_hash_by_nodeId(cls, label: str, nodeId: int, attrIgnoreList=None) -> str:
        """
        Calculates the hash_value sum over a given node. Use attrIgnoreList to specify attribute names that should be excluded when calculating the hash_value
        @param label: model label
        @param nodeId: the node ID
        @param attrIgnoreList: attributes to be ignored in the hash_value calculation
        @return: cypher query string
        """

        getModel = 'MATCH(n:{})'.format(label)
        where = 'WHERE ID(n) = {}'.format(nodeId)

        open_sub = 'CALL {WITH n'

        removeLabel = 'REMOVE n:{}'.format(label)

        # apply diffIgnore attributes if staged
        if attrIgnoreList == None:
            calc_fingerprint = 'with apoc.hashing.fingerprint(n) as hash_value RETURN hash'
        else:
            # define fucntion where quotationmarks "" or [] are added
            def surroundStrings(l):
                return ['"' + x + '"' for x in l]
            
            ignore_str = surroundStrings(attrIgnoreList)
            # define separator
            separator = ', '

            # join the contents of the list with the separator
            ignore_str = separator.join(ignore_str)

            # close the string with []
            ignore_str = '[' + ignore_str + ']'
 
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
        match = 'MATCH (n:{})-[r]->(c)'.format(label)
        where = 'WHERE ID(n) = {}'.format(parent_node_id)
        ret = 'RETURN ID(c), r.relType, c.EntityType, properties(c)'
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

    @classmethod
    def get_directed_path_by_nodeId(cls, node_id_start: int, node_id_target: int) -> str:
        """
        queries the path between two nodes
        @param node_id_start: node id of start node
        @param node_id_target: node id of target node
        @return: cypher query string
        """
        match_start = 'MATCH(n) WHERE ID(n) = {}'.format(node_id_start)
        match_target = 'MATCH(m) WHERE ID(m) = {}'.format(node_id_target)
        path = 'MATCH p = shortestPath((n)-[*..10]->(m))' # max path length is hardcoded to 10
        ret = 'RETURN p as path, NODES(p), RELATIONSHIPS(p)'
        return Neo4jFactory.BuildMultiStatement([match_start, match_target, path, ret])

    @classmethod
    def get_pattern_by_node_id(cls, node_id: int) -> str:
        """

        @param node_id:
        @return: cypher query string
        """
        match = 'MATCH pattern = (n)-[*..10]->(m)'
        where = 'WHERE ID(n) = {}'.format(node_id)
        ret = 'RETURN pattern'
        return Neo4jFactory.BuildMultiStatement([match, where, ret])

    @classmethod
    def get_outgoing_rel_types(cls, node_id: int):
        """
        Queries
        @param node_id:
        @return: cypher query string
        """
        match1 = 'match p = (n) Where ID(n)={}'.format(node_id)
        match2 = 'match (n)-[r]->(f)'
        ret = 'UNWIND r.relType as mylist RETURN mylist'
        return Neo4jFactory.BuildMultiStatement([match1, match2, ret])

    @classmethod
    def get_distinct_paths_from_node(cls, node_id: int) -> str:
        """
        Queries all distinct paths outgoing from a specified node
        @param node_id:
        @return: cypher query string
        """
        match1 = 'MATCH p = (n) WHERE ID(n)={}'.format(node_id)
        match2 = 'MATCH paths = (n)-[*..12]->(leaf)' # max length is set to 12!
        cond = 'WHERE NOT (leaf)-->()' # no outgoing edges
        ret = 'RETURN paths, NODES(paths), RELATIONSHIPS(paths)'
        return Neo4jFactory.BuildMultiStatement([match1, match2, cond, ret])

    @classmethod
    def get_primary_structure(cls, label: str) -> str:
        """
        Queries all nodes and edges involved in the primary structure
        @param label: model label
        @return: cypher query string
        """
        pattern = 'MATCH pattern = (n:{}}:PrimaryNode)<--(con)'.format(label)
        ret = 'RETURN pattern'
        return Neo4jFactory.BuildMultiStatement([pattern, ret])

    @classmethod
    def get_adjacency_primary(cls, label: str) -> str:
        """

        @param label:
        @return: cypher query string
        """
        match1 = 'MATCH (n:ts20210521T074802) WHERE Not n:SecondaryNode'
        match2 = 'MATCH (m:ts20210521T074802) WHERE Not m:SecondaryNode'
        ret = 'RETURN n.GlobalId as FromNodeGUID, m.GlobalId as ToNodeGUID, Exists((n)-->(m)) as connected'
        return Neo4jFactory.BuildMultiStatement([match1, match2, ret])

    @classmethod
    def get_adjacency_byNodeIds(cls, nodeIds) -> str:
        """

        @param nodeIds:
        @return: cypher query string
        """

        match1 = 'MATCH (n) WHERE ID(n) in {}'.format(nodeIds)
        match2 = 'MATCH (m) WHERE ID(m) in {}'.format(nodeIds)

        unwind1 = 'UNWIND n.GlobalId as fromGuid'
        unwind2 = 'UNWIND m.GlobalId as toGuid'

        ret = 'RETURN fromGuid as fromGuid, toGuid as toGuid, Exists((m) -->(n)) as connected'
        sort = 'Order by fromGuid ASC, toGuid ASC'
        return Neo4jFactory.BuildMultiStatement([match1, match2, unwind1, unwind2, ret, sort])
# ticket_PostEvent-VerifyParsedModel
# -- create a new method GetNumberOfNodesInGraph(cls, label) here --
