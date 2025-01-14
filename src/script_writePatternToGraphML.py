import networkx

from PatchManager.PatchService import PatchService


def write_graph():
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
        "WandTuer": ("ts20221001T100832", "ts20221001T100900"),
        "WandTuermodGuids": ("ts20221002T111302", "ts20221001T111540")
    }
    case_study = 'WandTuermodGuids'
    ts_init, ts_updated = testcases[case_study]

    # init service
    service = PatchService()
    patch = service.load_patch_from_json('Patch_init{}-updt{}.json'.format(ts_init, ts_updated))

    all_operations = networkx.Graph()
    for operation in patch.operations:

        graph = operation.get_nx_graph()
        all_operations = networkx.compose_all([all_operations, graph])

    networkx.write_graphml(G=all_operations, path="test2.graphml")


if __name__ == "__main__":
    write_graph()
