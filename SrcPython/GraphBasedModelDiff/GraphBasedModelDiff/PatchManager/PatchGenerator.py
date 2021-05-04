from GraphBasedModelDiff.PatchManager.Patch import Patch
from GraphBasedModelDiff.neo4jGraphDiff.DiffResult import DiffResult


class PatchGenerator:

    def __init__(self):
        self.patch: Patch = Patch()

    def create_patch_from_graph_diff(self, diff_res: DiffResult):
        """
        creates a patch from a given DiffResult object.
        The DiffResult is achieved by running the DfsIsomorphismCalculator
        @param diff_res:
        """

        # set time stamps
        self.patch.base_timestamp = diff_res.timestamp_init
        self.patch.resulting_timestamp =diff_res.timestamp_updated

    def to_json(self):
        raise NotImplementedError("not implemented yet. ")


