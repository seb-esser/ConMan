from pprint import pprint

import jsonpickle

from PatchManager.GraphBasedPatch import GraphBasedPatch
from PatchManager.Patch import Patch
from neo4jGraphDiff.GraphDelta import GraphDelta


def main():

    testcases = {
        "sleeperExample": ("ts20200202T105551", "ts20200204T105551"),
        "cuboid_differentSubgraphs": ("ts20210119T085406", "ts20210119T085407"),
        "cuboid_changedElevation": ("ts20210119T085408", "ts20210119T085409"),
        "cuboid_vs_cylinder": ("ts20210119T085410", "ts20210119T085411"),
        "cuboid_extruded_vs_BRep": ("ts20210119T085412", "ts20210119T085413"),
        "wall_column": ("ts20200713T083450", "ts20200713T083447"),
        "residential": ("ts20210219T121203", "ts20210219T121608"),
        "4x3_bridges": ("ts20210118T211240", "ts20210227T133609"),
        "Storey": ("ts20210521T074802", "ts20210521T074934"),
        "new_cuboid": ("ts20210623T091748", "ts20210623T091749"),
        "solibri": ("ts20121017T152740", "ts20121017T154702"),
        "CAM": ("ts20220715T135504", "ts20220715T135358"),
        "FirstStorey": ("ts20220930T111448", "ts20220930T111542"),
        "WandTuer": ("ts20221001T100832", "ts20221001T100900"),
        "WandTuermodGuids": ("ts20221002T111302", "ts20221001T111540"),
        "TW1-TW2": ("ts20240215T144400", "ts20240215T144950"),
        "ARC1-ARC2": ("ts20240214T141022", "ts20240214T171613"),
        "ARC2-ARC3": ("ts20240214T171613", "ts20240219T144637")
    }

    case_study = 'ARC1-ARC2'
    ts_init, ts_updated = testcases[case_study]

    path = 'Patch_init{}-updt{}.json'.format(ts_init, ts_updated)

    # load graph delta
    with open(path) as f:
        content = f.read()

    print("[INFO] loading patch json....")
    patch: GraphBasedPatch = jsonpickle.decode(content)

    print(patch)
    for sMod in patch.attribute_changes:
        print("SemModification:")
        print("PrimNode: {} - {}".format(sMod.path.get_start_node().attrs["EntityType"], sMod.path.get_start_node().attrs["GlobalId"]))
        print("ModifiedNode: {}".format(sMod.path.get_last_node().attrs["EntityType"]))
        print("Key: " + sMod.attribute_name)
        print("ValInit: {}".format(sMod.init_value))
        print("ValUpdt: {}".format(sMod.updated_value))
        print()


if __name__ == "__main__":
    main()
