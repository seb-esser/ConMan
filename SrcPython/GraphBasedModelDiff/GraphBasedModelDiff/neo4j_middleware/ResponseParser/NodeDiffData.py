from neo4jGraphDiff.Caption.SubstructureDiffResult import PropertyModification
from neo4j_middleware.ResponseParser.GraphPath import GraphPath


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

    def createPModDefinitions(self, nodeId_init: int, nodeId_updated: int, path_init: GraphPath, path_updated: GraphPath):
        """
        creates a PropertyModification instance out of the given object data
        @param nodeId_init: the node id of the modified node in the initial graph
        @param nodeId_updated: the node id of the modified node in the updated graph
        @param path_init: the path between the primary node and the modified one
        @param path_updated: the path between the primary node and the modified one
        @return:
        """
        lst: list[PropertyModification] = []

        for i in self.AttrsAdded.items():
            pm = PropertyModification(
                nodeId_init,
                nodeId_updated,
                attrName=i[0],
                modificationType="added",
                value_old=None,
                value_new=i[1])
            # add patterns to propertyModification instances
            pm.set_paths(path_init=path_init, path_updated=path_updated)

            lst.append(pm)

        for i in self.AttrsDeleted.items():
            pm = PropertyModification(
                nodeId_init,
                nodeId_updated,
                attrName=i[0],
                modificationType="deleted",
                value_old=i[1],
                value_new=None)
            # add patterns to propertyModification instances
            pm.set_paths(path_init=path_init, path_updated=path_updated)
            lst.append(pm)

        for i in self.AttrsModified.items():
            pm = PropertyModification(
                nodeId_init,
                nodeId_updated,
                attrName=i[0],
                modificationType="modified",
                value_old=i[1]['left'],
                value_new=i[1]['right'])
            # add patterns to propertyModification instances
            pm.set_paths(path_init=path_init, path_updated=path_updated)
            lst.append(pm)

        return lst
