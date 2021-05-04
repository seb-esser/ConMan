from PatchManager.Patch import Patch
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult


class PatchGenerator:

    def __init__(self):
        self.patch: Patch = Patch()

    def create_patch_from_graph_diff(self, diff_res: SubstructureDiffResult):
        """
        creates a patch from a given SubstructureDiffResult object.
        The SubstructureDiffResult is achieved by running the DfsIsomorphismCalculator
        @param diff_res:
        """

        # set time stamps
        self.patch.base_timestamp = diff_res.timestamp_init
        self.patch.resulting_timestamp = diff_res.timestamp_updated

    def to_json(self):
        raise NotImplementedError("not implemented yet. ")


