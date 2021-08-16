from typing import List

from neo4jGraphDiff.Caption.PropertyModification import PropertyModification
from neo4j_middleware.ResponseParser.GraphPath import GraphPath
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


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

    def createPModDefinitions(self, nodeId_init: int, nodeId_updated: int, pattern: GraphPattern):
        """
        creates a PropertyModification instance out of the given object data
        @param pattern:
        @param nodeId_init: the node id of the modified node in the initial graph
        @param nodeId_updated: the node id of the modified node in the updated graph
        @return:
        """
        lst: List[PropertyModification] = []

        for i in self.AttrsAdded.items():
            pm = PropertyModification(
                nodeId_init,
                nodeId_updated,
                attrName=i[0],
                modificationType="added",
                pattern=pattern,
                value_old=None,
                value_new=i[1])

            lst.append(pm)

        for i in self.AttrsDeleted.items():
            pm = PropertyModification(
                nodeId_init,
                nodeId_updated,
                attrName=i[0],
                modificationType="deleted",
                pattern=pattern,
                value_old=i[1],
                value_new=None)

            lst.append(pm)

        for i in self.AttrsModified.items():
            pm = PropertyModification(
                nodeId_init,
                nodeId_updated,
                attrName=i[0],
                modificationType="modified",
                pattern=pattern,
                value_old=i[1]['left'],
                value_new=i[1]['right'])

            lst.append(pm)

        return lst
