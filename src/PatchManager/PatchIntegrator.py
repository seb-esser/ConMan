import jsonpickle

from PatchManager.Patch import Patch
from neo4j_middleware import neo4jConnector


class PatchIntegrator(object):
    """ applies an incoming patch on a database """

    def __init__(self, connector: neo4jConnector):
        self.connector = connector

    def apply_patch(self, patch: Patch):
        """

        @param patch:
        @return:
        """

        # identify the graph, which the patch should be applied on
        target_graph = patch.base_timestamp

        # decode pMod and sMod operations
        operations = patch.operations
        for op in operations:
            print(op)

    @classmethod
    def from_json(cls, json_path):
        # js = jsonpickle.decode(json_path)
        raise NotImplementedError("not done yet")
