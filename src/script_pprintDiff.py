from pprint import pprint

import jsonpickle

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

    case_study = 'ARC1-ARC2-pure'
    ts_init, ts_updated = testcases[case_study]

    path = 'GraphDelta_init{}-updt{}.json'.format(ts_init, ts_updated)

    # load graph delta
    with open(path) as f:
        content = f.read()

    print("[INFO] loading delta json....")
    delta: GraphDelta = jsonpickle.decode(content)

    overall_sMod_pattern = GraphPattern()

    print("SMOD COUNT: {}".format(len(delta.property_updates)))
    for sMod in delta.property_updates:

        print("SemModification:")
        print("PrimNode: {}".format(sMod.pattern.get_entry_node().attrs["GlobalId"]))
        print("Key: " + sMod.attrName)
        print("ValInit: {}".format(sMod.valueOld))
        print("ValUpdt: {}".format(sMod.valueNew))
        print("UniquePath: ")
        arrow_vis_relaxed = sMod.pattern.to_arrows_visualization(create_relaxed_pattern=False)
        print(jsonpickle.encode(arrow_vis_relaxed, unpicklable=False))
        print("CYPHER UNIQUE PATH: ")
        print(sMod.pattern.to_cypher_match(entType_guid_only=True))
        if type(sMod.valueNew) in [int, float]:
            print("SET n{}.{} = {}".format(sMod.node_init.attrs["p21_id"], sMod.attrName, sMod.valueNew))
        else:
            print("SET n{}.{} = \"{}\"".format(sMod.node_init.attrs["p21_id"], sMod.attrName, sMod.valueNew))

        print("")

        # create overall pattern
        overall_sMod_pattern.paths.extend(sMod.pattern.paths)

    print("Overall SMOD Pattern")

    print(jsonpickle.encode(
        overall_sMod_pattern.to_arrows_visualization(create_relaxed_pattern=True),
        unpicklable=False))

    print(overall_sMod_pattern.to_cypher_match(entType_guid_only=True))
    for sMod in delta.property_updates:
        if type(sMod.valueNew) in [int, float]:
            print("SET n{}.{} = {}".format(sMod.node_init.attrs["p21_id"], sMod.attrName, sMod.valueNew))
        else:
            print("SET n{}.{} = \"{}\"".format(sMod.node_init.attrs["p21_id"], sMod.attrName, sMod.valueNew))

    print()

    print("Latex Table view")
    for sMod in delta.property_updates:
        print("{} & {} & {} & {} \\\\".format(sMod.node_init.attrs["p21_id"], sMod.attrName, sMod.valueOld, sMod.valueNew))

    print()
    print("TopoMOD COUNT: {}".format(len(delta.structure_updates)))
    for topoMod in delta.structure_updates:
        print("TopoModification: ")
        print("Parent: {} - {}".format(topoMod.parent.attrs["GlobalId"], topoMod.parent.attrs["EntityType"]))
        print("Child: {} - {}".format(topoMod.child.attrs["GlobalId"], topoMod.child.attrs["EntityType"]))
        print("OPERATION: {}".format(topoMod.modType))
        print()


if __name__ == "__main__":
    main()
