from neo4jGraphDiff.GraphDiff import GraphDiff
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


def main():

    connector = Neo4jConnector()
    connector.connect_driver()

    testcases = {"sleeperExample": ("ts20200202T105551", "ts20200204T105551"),
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
                 "CAM": ("ts20220715T135504", "ts20220715T135358")
                 }

    case_study = 'CAM'
    ts_init, ts_updated = testcases[case_study]

    print('Running Diff on case study: >{}<'.format(case_study))
    print("Do you really want to re-run the diff calculation? ")
    confirm = input("[y, n]")

    if confirm != "y":
        exit()

    connector.run_cypher_statement("Match(n:{})-[r:EQUIVALENT_TO]-(m:{}) DELETE r".format(ts_init, ts_updated))

    # get topmost entry nodes
    raw_init = connector.run_cypher_statement(
        """
        MATCH (n:PrimaryNode:{} {{EntityType: "IfcProject"}})
        RETURN ID(n), n.EntityType, PROPERTIES(n), LABELS(n)
        """.format(ts_init))
    raw_updated = connector.run_cypher_statement(
        """
        MATCH (n:PrimaryNode:{} {{EntityType: "IfcProject"}})
        RETURN ID(n), n.EntityType, PROPERTIES(n), LABELS(n)
        """.format(ts_updated))

    entry_init: NodeItem = NodeItem.from_neo4j_response(raw_init, False)[0]
    entry_updated: NodeItem = NodeItem.from_neo4j_response(raw_updated, False)[0]

    pDiff = GraphDiff(connector=connector, ts_init=ts_init, ts_updated=ts_updated)
    delta = pDiff.diff_subgraphs(entry_init, entry_updated)

    # connect equivalent nodes
    print('[INFO] building EQUIVALENT_TO edges ... ')
    pDiff.build_equivalent_to_edges()
    print('[INFO] building EQUIVALENT_TO edges: DONE. ')

    u_input = 'y'
    # u_input = input('Store delta object to json? [y, n]')

    if u_input == 'y':
        import jsonpickle
        print('saving delta ... ')
        f = open('GraphDelta_init{}-updt{}.json'.format(ts_init, ts_updated), 'w')
        f.write(jsonpickle.dumps(delta))
        f.close()
        print('saving delta: DONE. ')

    connector.disconnect_driver()


if __name__ == "__main__":
    main()


