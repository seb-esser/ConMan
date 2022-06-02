from PatchManager.PatchService import PatchService
from neo4j_middleware.neo4jConnector import Neo4jConnector


def main():
    connector = Neo4jConnector()
    connector.connect_driver()

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
        "solibri": ("ts20121017T152740", "ts20121017T154702")
    }

    case_study = 'cuboid_changedElevation'
    ts_init, ts_updated = testcases[case_study]

    # init new PatchService object handling all load and save operations
    service = PatchService()

    # load patch
    patch = service.load_patch_from_json('Patch_init{}-updt{}.json'.format(ts_init, ts_updated))

    # apply the patch
    service.apply_patch(patch, connector=connector)

    connector.disconnect_driver()


if __name__ == "__main__":
    main()
