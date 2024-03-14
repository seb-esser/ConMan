from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
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

    # pushout to be removed
    cy = """
    MATCH pa = (n:{})-[:rel*0..]->(m) 
    WHERE NOT EXISTS ((n)-[:EQUIVALENT_TO]-()) AND NOT EXISTS((m)-[:EQUIVALENT_TO]-()) 
    RETURN pa,  NODES(pa), RELATIONSHIPS(pa)
    """.format(ts_init)
    raw = connector.run_cypher_statement(cy)
    pattern_removed = GraphPattern.from_neo4j_response(raw)

    # pushout to be inserted
    cy = """
        MATCH pa = (n:{})-[:rel*0..]->(m) 
        WHERE NOT EXISTS ((n)-[:EQUIVALENT_TO]-()) AND NOT EXISTS((m)-[:EQUIVALENT_TO]-()) 
        RETURN pa,  NODES(pa), RELATIONSHIPS(pa)
        """.format(ts_updated)
    raw = connector.run_cypher_statement(cy)
    pattern_inserted = GraphPattern.from_neo4j_response(raw)

    glue = GraphPattern()
    context = GraphPattern()

    for node in pattern_inserted.get_unified_node_set():

        # check if glue is required
        cy = """
        MATCH pa = {}<-[:rel]-(a) WHERE EXISTS ((a)-[:EQUIVALENT_TO]-())         
        RETURN pa,  NODES(pa), RELATIONSHIPS(pa)
        """.format(node.to_cypher())
        raw_in = connector.run_cypher_statement(cy)

        cy = """
        MATCH pa = {0}-[:rel]->(a) WHERE EXISTS ((a)-[:EQUIVALENT_TO]-())         
        RETURN pa,  NODES(pa), RELATIONSHIPS(pa)
        """.format(node.to_cypher())
        raw_out = connector.run_cypher_statement(cy)

        if not len(raw_in) == 0:
            # get glue
            in_glue_pattern = GraphPattern.from_neo4j_response(raw_in)
            glue.paths.extend(in_glue_pattern.paths)

            # get context

            if in_glue_pattern.get_entry_node().get_node_type() in ["PrimaryNode", "ConnectionNode"]:
                in_context = GraphPattern([EdgeItem(in_glue_pattern.get_entry_node(), NodeItem(-1), -1)])
                context.paths.extend(in_context.paths)
                continue

            cy = """
            MATCH pa = {}<-[:rel*]-(p:PrimaryNode)
            WHERE EXISTS ((p)-[:EQUIVALENT_TO]-())         
            RETURN pa,  NODES(pa), RELATIONSHIPS(pa) LIMIT 1
            """.format(in_glue_pattern.paths[0].segments[0].start_node.to_cypher())

            raw = connector.run_cypher_statement(cy)
            in_context = GraphPattern.from_neo4j_response(raw)
            context.paths.extend(in_context.paths)

        elif not len(raw_out) == 0:
            out_glue_pattern = GraphPattern.from_neo4j_response(raw_out)
            glue.paths.extend(out_glue_pattern.paths)

            # get context

            if out_glue_pattern.get_entry_node().get_node_type() in ["PrimaryNode", "ConnectionNode"]:
                in_context = GraphPattern([EdgeItem(out_glue_pattern.get_entry_node(), NodeItem(-1), -1)])
                context.paths.extend(in_context.paths)
                continue

            cy = """
            MATCH pa = {}<-[:rel*]-(p:PrimaryNode)
            WHERE EXISTS ((p)-[:EQUIVALENT_TO]-())         
            RETURN pa,  NODES(pa), RELATIONSHIPS(pa) LIMIT 1
            """.format(out_glue_pattern.paths[0].segments[0].end_node.to_cypher())

            raw = connector.run_cypher_statement(cy)
            in_context = GraphPattern.from_neo4j_response(raw)
            context.paths.extend(in_context.paths)


        else:
            continue

    print(pattern_inserted)


if __name__ == "__main__":
    main()
