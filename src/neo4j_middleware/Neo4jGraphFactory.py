from .Neo4jFactory import Neo4jFactory


class Neo4jGraphFactory(Neo4jFactory):

    @classmethod
    def create_relationship(cls, source_node_id: int, target_node_id: int, rel_type: str) -> str:
        """
        Provides the cypher command to create a directed graph edge between two nodes
        specified by their node ids.
        @param source_node_id : node ID in the neo4j graph, on which the edge should start
        @param target_node_id: node ID in the neo4j graph, which the edge is pointing to
        @param rel_type: edge type
        @return cypher string to be executed using a connector instance.
        """
        match_source = 'MATCH(s) where ID(s) = {}'.format(source_node_id)
        match_target = 'MATCH(t) where ID(t) = "{}"'.format(target_node_id)
        merge = 'MERGE (s)-[:r {{ relType: \'{}\' }}]->(t)'.format(rel_type)
        return Neo4jFactory.BuildMultiStatement([match_source, match_target, merge])

    @classmethod
    def create_primary_node(cls, entity_id: str, entity_type: str, timestamp: str) -> str:
        """
        Provides the cypher command to create a primary node in the neo4j database.
        @param entity_id: param value for GlobalId attribute
        @param entity_type: reflection of data model class
        @param timestamp: identifier for a model
        @return: cypher command as str
        """
        create = 'CREATE(n:{}:PrimaryNode)'.format(timestamp)
        setGuid = 'SET n.GlobalId = "{}"'.format(entity_id)
        setEntityType = 'SET n.EntityType = "{}"'.format(entity_type)
        return_id = 'RETURN ID(n)'
        return Neo4jFactory.BuildMultiStatement([create, setGuid, setEntityType, return_id])

    @classmethod
    def add_attributes_by_node_id(cls, node_id: int, attributes: dict, timestamp: str) -> str:
        """
        Provides the cypher command to attach a given dictionary to a node specified by its node id
        @param node_id: node in the neo4j graph
        @param attributes: dictionary
        @param timestamp: identifier for a model
        @return: cypher command as str
        """
        match = 'MATCH(n:{}) WHERE ID(n) = {}'.format(timestamp, node_id)
        attrs = []
        for attr, val in attributes.items():
            if isinstance(val, (str, tuple)):
                add_param = 'SET n.{} = "{}"'.format(attr, val)
                attrs.append(add_param)
            elif isinstance(val, (int, float, complex)):
                add_param = 'SET n.{} = {}'.format(attr, val)
                attrs.append(add_param)
            elif val is None:
                add_param = 'SET n.{} = "{}"'.format(attr, 'None')
                attrs.append(add_param)
            else:
                add_param = 'SET n.{} = "{}"'.format(attr, 'None')
                attrs.append(add_param)
                # raise Exception('ERROR when adding attributes to existing node. check your inputs. \n '
                #                 '\t {} \t {}'.format(attr, val))
        returnID = 'RETURN n'

        return Neo4jFactory.BuildMultiStatement([match] + attrs + [returnID])

    @classmethod
    def create_secondary_node(cls, parent_id: int, entity_type: str, rel_attrs: dict, timestamp: str) -> str:
        """
        Provides the cypher command to attach a given dictionary to a node specified by its node id
        @param parent_id: source node, which is referenced by the newly created secondary node. Can be set to None
        @param entity_type: reflection of data model class
        @param rel_attrs: dictionary to be attached to the edge
        @param timestamp: identifier for a model
        @return: cypher command as str
        """

        create = 'CREATE (n:SecondaryNode:{} {{EntityType: "{}" }})'.format(timestamp, entity_type)

        if parent_id is not None:
            match = 'MATCH (p) WHERE ID(p) = {}'.format(parent_id)
            merge = 'MERGE (p)-[r:rel]->(n)'

            attrs = []
            for attr, val in rel_attrs.items():
                if isinstance(val, str):
                    add_param = 'SET r.{} = "{}"'.format(attr, val)
                    attrs.append(add_param)
                elif isinstance(val, (int, float, complex)):
                    add_param = 'SET r.{} = {}'.format(attr, val)
                    attrs.append(add_param)
        else:
            match = ""
            merge = ""

        returnID = 'RETURN ID(n)'

        return Neo4jFactory.BuildMultiStatement([match, create, merge] + attrs + [returnID])

    @classmethod
    def create_list_node(cls, parent_id: int, rel_type: str, timestamp: str) -> str:
        """
        Provides the cypher command to attach a given dictionary to a node specified by its node id
        @param parent_id: source node, the new node is merged to
        @param rel_type: reflection of association attribute name provided by the underlying data model
        @param timestamp: identifier for a model
        @return: cypher command as str
        """
        match = 'MATCH (p) WHERE ID(p) = {}'.format(parent_id)
        create = 'CREATE (n:ListNode:{})'.format(timestamp)
        setEntityType = 'SET n.EntityType = "{}"'.format("NestedList")
        merge = 'MERGE (p)-[:r {{ relType: \'{}\' }}]->(n)'.format(rel_type)
        returnID = 'RETURN ID(n)'
        return Neo4jFactory.BuildMultiStatement([match, create, setEntityType, merge, returnID])

    @classmethod
    def create_list_item_node(cls, parent_id: int, item_no: int, timestamp: str) -> str:
        """
        Provides the cypher command to attach a given dictionary to a node specified by its node id
        @param parent_id: source node, the new node is merged to
        @param item_no: list item no
        @param timestamp: identifier for a model
        @return: cypher command as str
        """
        match = 'MATCH (p) WHERE ID(p) = {}'.format(parent_id)
        create = 'CREATE (n:ListItemNode:{})'.format(timestamp)
        setEntityType = 'SET n.EntityType = "{}"'.format("ListItem")
        merge = 'MERGE (p)-[:listItem {{ relType: \'{}\' }}]->(n)'.format(item_no)
        returnID = 'RETURN ID(n)'
        return Neo4jFactory.BuildMultiStatement([match, create, setEntityType, merge, returnID])

    @classmethod
    def merge_rooted_node_with_owner_history(cls, owner_history_guid: str, my_node_id: int, timestamp: str) -> str:
        """
        Provides the cypher command to connect a given node with the owner history.
        This method is used in the IfcJSON parser
        @param owner_history_guid:
        @param my_node_id:
        @param timestamp:identifier for a model
        @return: cypher command as str
        """
        match = 'MATCH (p:{}) WHERE p.GlobalId = "{}"'.format(timestamp, owner_history_guid)
        matchOwn = 'MATCH (me) WHERE ID(me) = {}'.format(my_node_id)
        merge = 'MERGE (me)-[:r {{ relType: \'{}\' }}]->(p)'.format('IfcOwnerHistory')
        returnID = 'RETURN ID(me)'
        return Neo4jFactory.BuildMultiStatement([match, matchOwn, merge, returnID])

    @classmethod
    def create_connection_node(cls, rel_guid: str, entity_type: str, timestamp: str):
        """
        Provides the cypher command to create a connection node. It represents a one-to-many rel or many-to-many rel.
        @param rel_guid: the unique identifier
        @param entity_type: the class name from the underlying data model
        @param timestamp: identifier for a model
        @return:cypher command as str
        """
        create = 'CREATE(n:ConnectionNode:{})'.format(timestamp)
        setGuid = 'SET n.GlobalId = "{}"'.format(rel_guid)
        setEntityType = 'SET n.EntityType = "{}"'.format(entity_type)
        returnID = 'RETURN ID(n)'
        return Neo4jFactory.BuildMultiStatement([create, setGuid, setEntityType, returnID])

    @classmethod
    def merge_con_with_primary_node(cls, obj_rel_guid: str, target_node_guid: str, rel_type: str,
                                    inverse_rel_type: str,
                                    timestamp: str) -> str:
        """
        Provides the cypher command to merge a connection node with a primary node
        @param rel_type:
        @param obj_rel_guid:
        @param target_node_guid:
        @param inverse_rel_type:
        @param timestamp:
        @return:
        """
        matchObjRel = 'MATCH (objrel:{}) WHERE objrel.globalId = "{}"'.format(timestamp, obj_rel_guid)
        matchRootedObj = 'MATCH (rooted:{}) WHERE rooted.globalId = "{}"'.format(timestamp, target_node_guid)
        merge1 = 'MERGE (objrel)-[:r {{ relType: \'{}\' }}]->(rooted)'.format(rel_type)
        merge2 = 'MERGE (objrel)<-[:r {{ relType: \'{}\' }}]-(rooted)'.format(inverse_rel_type)
        returnID = 'RETURN ID(rooted)'
        return Neo4jFactory.BuildMultiStatement([matchObjRel, matchRootedObj, merge1, merge2, returnID])

    @classmethod
    def merge_on_p21(cls, from_p21, to_p21, rel_attrs, timestamp):
        """
        Provides the cypher command to merge two nodes based on their P21 vals
        @param from_p21:
        @param to_p21:
        @param rel_attrs:
        @param timestamp:
        @return: cypher command as str
        """
        from_node = 'MATCH (source:{}) WHERE source.p21_id = {}'.format(timestamp, from_p21)
        to_node = 'MATCH (target:{}) WHERE target.p21_id = {}'.format(timestamp, to_p21)
        merge = 'MERGE (source)-[r:rel ]->(target)'
        attrs = []
        for attr, val in rel_attrs.items():
            if isinstance(val, str):
                add_param = 'SET r.{} = "{}"'.format(attr, val)
                attrs.append(add_param)
            elif isinstance(val, (int, float, complex)):
                add_param = 'SET r.{} = {}'.format(attr, val)
                attrs.append(add_param)
        returnID = 'RETURN ID(source), ID(target)'
        return Neo4jFactory.BuildMultiStatement([from_node, to_node, merge] + attrs + [returnID])

    @classmethod
    def merge_on_node_ids(cls, node_id_from: int, node_id_to: int, rel_type: str = 'DEFAULT_CONNECTION') -> str:
        """
        Provides the cypher command to merge two nodes by their IDs
        @param node_id_from:
        @param node_id_to:
        @param rel_type:
        @return:
        """
        fromNode = 'MATCH (s) WHERE ID(s) = {}'.format(node_id_from)
        toNode = 'MATCH (t) WHERE ID(t) = {}'.format(node_id_to)
        merge = 'MERGE (s)-[:r {{ relType: \'{}\' }}]->(t)'.format(rel_type)
        return Neo4jFactory.BuildMultiStatement([fromNode, toNode, merge])

    @classmethod
    def delete_node_by_node_id(cls, node_id: int):
        """
        Provides the cypher command to delete a node specified by its node id
        @param node_id: node id in neo4j graph
        @return: cypher command as str
        """
        match = 'MATCH (n) WHERE ID(n) = {}'.format(node_id)
        detach = 'DETACH'
        delete = 'DELETE n'
        return Neo4jFactory.BuildMultiStatement([match, detach, delete])