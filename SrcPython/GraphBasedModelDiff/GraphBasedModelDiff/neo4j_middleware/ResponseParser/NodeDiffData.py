
class NodeDiffData:
    """decodes the neo4j response into an object """

    def __init__(self, unchanged, modified, added, deleted): 
        self.AttrsUnchanged = unchanged
        self.AttrsModified = modified
        self.AttrsAdded = added
        self.AttrsDeleted = deleted

    @classmethod
    def fromNeo4jResponse(cls, raw):
        ret_val = cls(raw[0][0]['inCommon'], raw[0][0]['different'] ,raw[0][0]['rightOnly'], raw[0][0]['leftOnly'] )
        return ret_val

    def __str__(self): 
        return 'unchanged: {}, modified: {}, added: {}, deleted: {}'.format(self.AttrsUnchanged, self.AttrsModified, self.AttrsAdded, self.AttrsDeleted)

    def __repr__(self):
        return 'NodeDiffData object'

    def nodesAreSimilar(self): 
        """ reports if the diffed nodes are similar based in their attributes """
        if self.AttrsAdded == {} and self.AttrsDeleted == {} and self.AttrsModified == {}:
            return True
        else:
            return False

    def nodesHaveUpdatedAttributeValues(self):
        """ reports if the diffed nodes share the same attributes but with different values """
        if self.AttrsModified != {}:
            return True
        else:
            return False

    def nodesHaveAddedDeletedAttributes(self):
        if self.AttrsAdded != {} or self.AttrsDeleted != {}:
            return True
        else:
            return False
