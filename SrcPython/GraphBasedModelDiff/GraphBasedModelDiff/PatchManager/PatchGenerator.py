from PatchManager.Patch import Patch
from neo4jGraphDiff.Caption.ResultGenerator import ResultGenerator
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult


class PatchGenerator:

    def __init__(self):
        self.patch: Patch = Patch()

    def create_patch_from_graph_diff(self, res: ResultGenerator):
        """
        creates a patch from a given SubstructureDiffResult object.
        The SubstructureDiffResult is achieved by running the DfsIsomorphismCalculator
        @param res:
        """

        # set time stamps
        self.patch.base_timestamp = res.timestamp_init
        self.patch.resulting_timestamp = res.timestamp_updated

        # --- Secondary structure modifications ---
        for p_mod in res.ResultComponentDiff:
            struc_mods = p_mod.StructureModifications
            prop_mods = p_mod.propertyModifications


        # --- Structural modifications ---

        # primary structure modifications
        for added in res.ResultRooted['added'].items():
            print(added)
            # serialize the root node

            # serialize the entire substructure under the root node


        for deleted in res.ResultRooted['deleted'].items():
            print(deleted)
            # serialize the root node

            # serialize how the substructure should be handled

        # secondary structure modifications




    def to_json(self):
        raise NotImplementedError("not implemented yet. ")


