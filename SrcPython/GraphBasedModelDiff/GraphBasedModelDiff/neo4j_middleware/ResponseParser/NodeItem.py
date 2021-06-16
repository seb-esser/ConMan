from neo4j_middleware.Neo4jFactory import Neo4jFactory


class NodeItem:
    """
    reflects the node structure from neo4j
    """

    def __init__(self, id: int, relType: str, entityType: str = None, nodeType: str = None):
        """

        @param id: node id
        @param relType: relType of edge pointing to this node
        @param entityType: the reflected Ifc Entity name
        """
        self.id = id
        self.entityType = entityType
        self.hash_value = None
        self.relType = relType
        self.attrs = None
        self.nodeType = nodeType

    def set_hash(self, hash_val: str):
        self.hash_value = hash_val

    def get_hash(self):
        return self.hash_value

    def __repr__(self):
        return 'NodeItem: id: {} EntityType: {}'.format(self.id, self.entityType)

    def __eq__(self, other):
        """
        implements a comparison function. matching by node id
        @param other:
        @return:
        """
        if self.id == other.id:
            return True
        else:
            return False

    @classmethod
    def fromNeo4jResponseWithRel(cls, raw: str) -> list:
        ret_val = []
        for inst in raw:
            child = cls(int(inst[0]), inst[1]['relType'], inst[2])
            if 'listItem' in inst[1]:
                child.relType = inst[1]['relType'] + '__listItem{}'.format(inst[1]['listItem'])
            attrs = inst[3]
            child.attrs = attrs
            ret_val.append(child)
        return ret_val

    @classmethod
    def fromNeo4jResponseWouRel(cls, raw: str) -> list:
        ret_val = []
        for inst in raw:
            child = cls(id=int(inst[0]), relType=None, entityType=inst[1])
            attrs = inst[2]
            child.attrs = attrs
            ret_val.append(child)
        return ret_val

    @classmethod
    def fromNeo4jResponse(cls, raw: str) -> list:
        """
        creates a List of NodeItem instances from a given neo4j response
        @param raw: neo4j response string
        @return:
        """
        ret_val = []
        for node_raw in raw:
            node = cls(int(node_raw.id), None, None)
            node.setNodeAttributes(node_raw._properties)
            node.entityType = node.attrs['EntityType']
            ret_val.append(node)

        return ret_val

    def setNodeAttributes(self, attrs):
        """
        assigns attributes to node item
        @param attrs: dict or list
        @return: nothing
        """
        if isinstance(attrs, list):
            d = attrs[0]
            self.attrs = d
        else:
            self.attrs = attrs

    def tidy_attrs(self):
        """
        removes entityType and p21_id from attr dict
        @return:
        """
        self.attrs.pop("EntityType", None)
        self.attrs.pop("p21_id", None)
        self.attrs.pop('relType', None)

        # remove attrs that have a none value assigned
        cleared_dict = {}
        for key, val in self.attrs.items():
            if val != 'None':
                cleared_dict[key] = val
            if key in ['Coordinates', 'DirectionRatios']:
                cleared_dict[key] = eval(val)
        self.attrs = cleared_dict

    def to_cypher(self, timestamp: str = None, node_identifier:str = None):
        """
        returns a cypher query fragment to search for this node with semantics
        @param timestamp: specify in which model you'd like to search for the node
        @param node_identifier:
        @return:
        """
        if node_identifier is None:
            node_identifier = 'n'
        if timestamp is None:
            ts = ''
        else:
            ts = ': {}'.format(timestamp)

        # remove p21_id attribute
        cleaned_node_attrs = self.attrs
        cleaned_node_attrs.pop('p21_id', None)

        return '({0}{1} {2})'.format(node_identifier, ts, Neo4jFactory.formatDict(self.attrs))

