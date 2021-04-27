class NodeItem:
    """
    reflects the node structure from neo4j
    """

    def __init__(self, id, relType, entityType= None):
        self.id = id
        self.entityType = entityType
        self.hash = None
        self.relType = relType
        self.attrs = None
        
    def setHash(self, hash): 
        self.hash = hash

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
        self.attrs = attrs

