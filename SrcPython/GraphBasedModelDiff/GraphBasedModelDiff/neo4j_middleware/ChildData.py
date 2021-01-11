class ChildData:
    """description of class"""

    def __init__(self, id, relType, entityType= None):
        self.id = id
        self.entityType = entityType
        self.hash = None
        self.relType = relType
        
    def setHash(self, hash): 
        self.hash = hash

    def __repr__(self):
        return 'ChildData: id: {} nodeType: {} relType = {} hash: {}'.format(self.id, self.NodeType, self.relType, self.hash)


