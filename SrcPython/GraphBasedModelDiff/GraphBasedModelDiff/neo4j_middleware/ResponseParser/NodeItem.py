class NodeItem:
    """
    reflects the node structure from neo4j
    """

    def __init__(self, id: int, relType: str, entityType: str = None):
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

    def set_hash(self, hash_val: str):
        self.hash_value = hash_val

    def get_hash(self):
        return self.hash_value

    def __repr__(self):
        return 'NodeItem: id: {} entityType: {}'.format(self.id, self.entityType)

    @classmethod
    def fromNeo4jResponseWithRel(cls, raw: str) -> list:
        ret_val = []
        for inst in raw:
            child = cls(int(inst[0]), inst[1], inst[2])
            ret_val.append(child)
        return ret_val

    @classmethod
    def fromNeo4jResponseWouRel(cls, raw: str) -> list:
        ret_val = []
        for inst in raw:
            child = cls(id=int(inst[0]), relType=None, entityType=inst[1])
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
            node.entityType = node.attrs['entityType']
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
        self.attrs.pop("entityType", None)
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
