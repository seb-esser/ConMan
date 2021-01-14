


class NodeDiffData:
    """description of class"""

    def __init__(self, unchanged, modified, added, deleted): 
        self.AttrsUnchanged = unchanged
        self.AttrsModified = modified
        self.AttrsAdded = added
        self.AttrsDeleted = deleted

    @classmethod
    def fromNeo4jResponse(cls, raw):
        ret_val = cls(raw[0][0]['inCommon'], raw[0][0]['different'],raw[0][0]['rightOnly'], raw[0][0]['leftOnly'] )
        return ret_val

    def __str__(self): 
        print('unchanged: {}'.format(self.AttrsUnchanged))
        print('modified: {}'.format(self.AttrsModified))
        print('added: {}'.format(self.AttrsAdded))
        print('deleted: {}'.format(self.AttrsDeleted))
    
    def __repr__(self):
        return 'NodeDiffData object'

    def nodesAreSimilar(self): 
        """ reports if the diffed nodes are similar based in their attributes """
        if (self.AttrsAdded == {} and self.AttrsDeleted == {} and self.AttrsModified == {} ):
            return True
        else:
            return False


    def nodesHaveUpdatedAttrs(self):
        """ reports if the diffed nodes share the same attributes but with different values """
        if (self.AttrsModified != {} and self.AttrsDeleted == {} and self.AttrsModified == {}):
            return True
        else:
            return False