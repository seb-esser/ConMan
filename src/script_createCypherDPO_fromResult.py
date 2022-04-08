import jsonpickle

from PatchManager.DoublePushOut import DoublePushOut
from PatchManager.Patch import Patch
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum
from neo4jGraphDiff.GraphDelta import GraphDelta
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


def main():
    ts_init = "ts20210623T091748"
    ts_updated = "ts20210623T091749"

    connector = Neo4jConnector()
    connector.connect_driver()

    # load graph delta
    with open('GraphDelta_init{}-updt{}.json'.format(ts_init, ts_updated)) as f:
        content = f.read()

    print("[INFO] loading delta json....")
    result: GraphDelta = jsonpickle.decode(content)
    print("[INFO] loading delta json: DONE.")

    update_patch = Patch()

    s_mods = result.structure_updates

    for s_mod in s_mods:
        guid = s_mod.child.attrs["GlobalId"]

        if s_mod.modType == StructuralModificationTypeEnum.ADDED:
            ts = ts_updated
        elif s_mod.modType == StructuralModificationTypeEnum.DELETED:
            ts = ts_init
        else:
            raise Exception("Modification type has not been specified properly. ")

        # generate PushOut Pattern
        cy = """
            MATCH pa = (n:PrimaryNode:{0} {{GlobalId: \"{1}\"}})-[:rel*..10]->(sec:SecondaryNode:{0})
            WHERE NOT (sec)-[:SIMILAR_TO]-() 
            RETURN pa,  NODES(pa), RELATIONSHIPS(pa)
            """.format(ts, guid)
        print(cy)
        raws = connector.run_cypher_statement(cy)
        push_out_pattern = GraphPattern.from_neo4j_response(raws)

        # generate context pattern
        context_pattern = GraphPattern([])

        # get the context for primary embedding
        cy = "MATCH pa = {}<-[:rel]-(c) RETURN pa, NODES(pa), RELATIONSHIPS(pa)".format(
            s_mod.child.to_cypher(skip_labels=True))
        raw = connector.run_cypher_statement(cy)
        context: GraphPattern = GraphPattern.from_neo4j_response(raw)
        context_pattern.paths.extend(context.paths)

        # get all context paths for secondary nodes
        nodes_pushed_out = push_out_pattern.get_unified_node_set()
        for n in nodes_pushed_out:
            cy_equ_neighbor = "match p = (n)-[r:rel]->(e)-[:SIMILAR_TO]-() WHERE ID(n) = {} return e".format(n.id)
            raw_neighbor = connector.run_cypher_statement(cy_equ_neighbor)
            if raw_neighbor != []:
                ref_node = NodeItem.from_neo4j_response(raw_neighbor[0])[0]
                # get "first visited from"
                parent_node = result.node_matching_table.get_parent_primaryNode(ref_node)

                # calculate shortest path
                cy = "MATCH {0}, {1}, p = SHORTESTPATH({2}-[:rel*]->{3}) RETURN p, NODES(p), RELATIONSHIPS(p)".format(
                    parent_node.to_cypher(),
                    ref_node.to_cypher(),
                    parent_node.to_cypher(skip_labels=True, skip_attributes=True),
                    ref_node.to_cypher(skip_labels=True, skip_attributes=True))
                raw = connector.run_cypher_statement(cy)
                context: GraphPattern = GraphPattern.from_neo4j_response(raw)
                context_pattern.paths.append(context.paths[0])

        # finally compile DPO rule
        lhs = None
        interface = None
        rhs = None

        if s_mod.modType == StructuralModificationTypeEnum.ADDED:
            # construct lhs
            lhs = context_pattern
            # construct interface
            interface = context_pattern
            # construct rhs
            # ToDo: the edges connecting the context and the pushout are not yet considered!
            context_paths = context_pattern.paths
            pushout_paths = push_out_pattern.paths
            rhs = GraphPattern(paths=context_paths + pushout_paths)

        dpo_rule = DoublePushOut(lhs=lhs, i=interface, rhs=rhs)
        update_patch.operations.append(dpo_rule)

    # print results
    print(update_patch)
    print(update_patch.operations[0].right_hand_side.to_cypher_match())

    # finally disconnect
    connector.disconnect_driver()


if __name__ == "__main__":
    main()
