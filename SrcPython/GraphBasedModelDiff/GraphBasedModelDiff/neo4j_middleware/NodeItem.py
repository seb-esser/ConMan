class NodeItem:
    """
    reflects the node structure from neo4j
    """

    def __init__(self, id, relType, entityType=None):
        self.id = id
        self.entityType = entityType
        self.hash = None
        self.relType = relType
        self.attrs = None

    def setHash(self, hash):
        self.hash = hash

    def get_hash(self):
        return self.hash

    def __repr__(self):
        return 'NodeItem: id: {} entityType: {}'.format(self.id, self.entityType)

    @classmethod
    def fromNeo4jResponseWithRel(cls, raw):
        ret_val = []
        for inst in raw:
            child = cls(inst[0], inst[1], inst[2])
            ret_val.append(child)
        return ret_val

    @classmethod
    def fromNeo4jResponseWouRel(cls, raw):
        ret_val = []
        for inst in raw:
            child = cls(id=inst[0], relType=None, entityType=inst[1])
            ret_val.append(child)
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

        self.attrs = cleared_dict
