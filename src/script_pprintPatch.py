from pprint import pprint

import jsonpickle

from PatchManager.GraphBasedPatch import GraphBasedPatch
from PatchManager.Patch import Patch
from neo4jGraphDiff.GraphDelta import GraphDelta
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


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
        "ARC2-ARC3": ("ts20240214T171613", "ts20240219T144637"),
        "ARC1-ARC2-pure": ("ts20240220T112536", "ts20240220T112601"),
        "ARC2-ARC3-pure": ("ts20240220T112601", "ts20240220T112845")
    }

    case_study = 'ARC2-ARC3-pure'
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

    overall_push_out = GraphPattern()
    overall_glue = GraphPattern()
    overall_context = GraphPattern()
    for topoMod in patch.operations:
        print("TopoModification:")
        print("PushOut")
        print(jsonpickle.encode(topoMod.push_out_pattern.to_arrows_visualization(), unpicklable=False))
        overall_push_out.paths.extend(topoMod.push_out_pattern.paths)

        print("Context")
        print(jsonpickle.encode(topoMod.context_pattern.to_arrows_visualization(), unpicklable=False))
        overall_context.paths.extend(topoMod.context_pattern.paths)

        print("Glue")
        print(jsonpickle.encode(topoMod.gluing_pattern.to_arrows_visualization(), unpicklable=False))
        overall_glue.paths.extend(topoMod.gluing_pattern.paths)

    print("Overall PushOut")
    print(jsonpickle.encode(overall_push_out.to_arrows_visualization(), unpicklable=False))
    print(overall_push_out.to_cypher_merge())
    print("Overall Context")
    print(jsonpickle.encode(overall_context.to_arrows_visualization(create_relaxed_pattern=True), unpicklable=False))
    print(overall_context.to_cypher_match())
    print("Overall Glue")
    print(jsonpickle.encode(overall_glue.to_arrows_visualization(create_relaxed_pattern=True), unpicklable=False))
    print(overall_glue.to_cypher_merge())


if __name__ == "__main__":
    main()
