import jsonpickle

from PatchManager.DoublePushOut import DoublePushOut
from PatchManager.Patch import Patch
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum
from neo4jGraphDiff.GraphDelta import GraphDelta
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class DPOService:
    def __init__(self, ts_init: str, ts_updated: str):
        self.ts_init: str = ts_init
        self.ts_updated: str = ts_updated

        # load graph delta
        with open('GraphDelta_init{}-updt{}.json'.format(ts_init, ts_updated)) as f:
            content = f.read()

        print("[INFO] loading delta json....")
        self.result: GraphDelta = jsonpickle.decode(content)
        print("[INFO] loading delta json: DONE.")

    def generate_DPO_patch(self, connector) -> Patch:

        patch = Patch()

        # get all structural modifications
        s_mods = self.result.structure_updates

        # loop over structural modifications
        for s_mod in s_mods:
            guid = s_mod.child.attrs["GlobalId"]

            if s_mod.modType == StructuralModificationTypeEnum.ADDED:
                ts = self.ts_updated
            elif s_mod.modType == StructuralModificationTypeEnum.DELETED:
                ts = self.ts_init
            else:
                raise Exception("Modification type has not been specified properly. ")

            # generate pushOut Pattern
            cy = """
                   MATCH pa = (n:PrimaryNode:{0} {{GlobalId: \"{1}\"}})-[:rel*..10]->(sec:SecondaryNode:{0})
                   WHERE NOT (sec)-[:SIMILAR_TO]-() 
                   RETURN pa,  NODES(pa), RELATIONSHIPS(pa)
                   """.format(ts, guid)
            raws = connector.run_cypher_statement(cy)
            push_out_pattern = GraphPattern.from_neo4j_response(raws)

            # generate context pattern
            context_pattern = GraphPattern()

            # generate gluing pattern
            gluing_pattern = GraphPattern()

            # get the embed for primary embedding
            cy = "MATCH {}<-[:rel]-(c:ConnectionNode) " \
                 "MATCH p = (c)-[:rel]->(prmN) WHERE NOT prmN = {} RETURN p, NODES(p), RELATIONSHIPS(p)".format(
                s_mod.child.to_cypher(skip_labels=True), s_mod.child.to_cypher(skip_labels=True, skip_attributes=True))

            raw = connector.run_cypher_statement(cy)
            prim_context: GraphPattern = GraphPattern.from_neo4j_response(raw)
            context_pattern.paths.extend(prim_context.paths)

            # get the gluing between primary push out and primary embed
            cy = "MATCH p= {}<-[:rel]-(c:ConnectionNode) " \
                 "RETURN p, NODES(p), RELATIONSHIPS(p)".format(
                s_mod.child.to_cypher(skip_labels=True), s_mod.child.to_cypher(skip_labels=True, skip_attributes=True))

            raw = connector.run_cypher_statement(cy)
            prim_gluing: GraphPattern = GraphPattern.from_neo4j_response(raw)
            gluing_pattern.paths.extend(prim_gluing.paths)

            # get all embed paths for secondary nodes
            nodes_pushed_out = push_out_pattern.get_unified_node_set()

            for n in nodes_pushed_out:
                cy_equ_neighbor = "match p = (n)-[r:rel]->(e)-[:SIMILAR_TO]-() WHERE ID(n) = {} return e".format(n.id)
                raw_neighbor = connector.run_cypher_statement(cy_equ_neighbor)

                # check if the newly created node has a relationship to another node
                # that is already present in the target graph
                if raw_neighbor != []:
                    context_node = NodeItem.from_neo4j_response(raw_neighbor[0])[0]
                    # get "first visited from"
                    parent_node = self.result.node_matching_table.get_parent_primaryNode(context_node)

                    # calculate the shortest path
                    cy = "MATCH {0}, {1}, p = SHORTESTPATH({2}-[:rel*]->{3}) RETURN p, NODES(p), RELATIONSHIPS(p)".format(
                        parent_node.to_cypher(),
                        context_node.to_cypher(),
                        parent_node.to_cypher(skip_labels=True, skip_attributes=True),
                        context_node.to_cypher(skip_labels=True, skip_attributes=True))
                    raw = connector.run_cypher_statement(cy)
                    embed: GraphPattern = GraphPattern.from_neo4j_response(raw)
                    context_pattern.paths.append(embed.paths[0])

                    # calculate the gluing edge connecting embed and push out
                    cy = "MATCH p = {}-[r:rel]->{} RETURN p, NODES(p), RELATIONSHIPS(p)".format(
                        n.to_cypher(skip_attributes=False, skip_labels=False),
                        context_node.to_cypher(skip_attributes=False, skip_labels=False))
                    raw = connector.run_cypher_statement(cy)
                    glue: GraphPattern = GraphPattern.from_neo4j_response(raw)

                    # add gluing edge
                    gluing_pattern.paths.append(glue.paths[0])

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
                context_paths = context_pattern.paths
                pushout_paths = push_out_pattern.paths
                gluing_paths = gluing_pattern.paths

                paths = context_paths + pushout_paths + gluing_paths
                rhs = GraphPattern(paths=paths)

            elif s_mod.modType == StructuralModificationTypeEnum.DELETED:
                # -- construct lhs --
                context_paths = context_pattern.paths
                pushout_paths = push_out_pattern.paths
                gluing_paths = gluing_pattern.paths

                print(gluing_pattern.to_cypher_match())
                print(push_out_pattern.to_cypher_match())

                paths = context_paths + pushout_paths + gluing_paths
                lhs = GraphPattern(paths=paths)

                # -- construct rhs --
                rhs = context_pattern
                # -- construct interface --
                interface = context_pattern

            # tidy attributes (e.g., p21 id, etc)
            lhs.tidy_node_attributes()
            interface.tidy_node_attributes()
            rhs.tidy_node_attributes()

            dpo_rule = DoublePushOut(lhs=lhs, i=interface, rhs=rhs)

            # add rule to patch object
            patch.operations.append(dpo_rule)

        return patch

