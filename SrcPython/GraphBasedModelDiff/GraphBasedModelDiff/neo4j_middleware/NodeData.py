class NodeData:
    """description of class"""

    def __init__(self, id, relType, entityType= None):
        self.id = id
        self.entityType = entityType
        self.hash = None
        self.relType = relType
        
    def setHash(self, hash): 
        self.hash = hash

    def __repr__(self):
        return 'NodeData: id: {} nodeType: {} relType = {} hash: {}'.format(self.id, self.NodeType, self.relType, self.hash)

    @classmethod
    def fromNeo4jResponse(cls, raw):
        ret_val = []
        for inst in raw: 
            child = cls(inst[0], inst[1], inst[2]) 
            ret_val.append(child)
        return ret_val
