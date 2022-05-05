import jsonpickle

from PatchManager.Patch import Patch
from PatchManager.TransformationRule import TransformationRule
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class PatchService:
    """
    manages loading and saving of patches and can apply a patch
    """
    def __init__(self):
        self.delta = None

    @classmethod
    def from_existing_delta(cls, delta):
        """
        creates PatchService object from existing delta object without loading any jsons
        @param delta:
        @return:
        """
        inst = cls()
        inst.delta = delta
        return inst

    def load_delta(self, path: str):
        """
        load delta from json
        @param path:
        @return:
        """
        # load graph delta
        with open(path) as f:
            content = f.read()

        print("[INFO] loading delta json....")
        self.delta = jsonpickle.decode(content)
        print("[INFO] loading delta json: DONE.")

    def generate_DPO_patch(self, connector) -> Patch:
        """
        produces a patch from a given delta
        @param connector: the neo4j connector instance
        @return: the patch object
        """

        print("[INFO] generate patch ....")
        patch = Patch()

        try:
            ts_init = self.delta.ts_init
            ts_updated = self.delta.ts_updated
        except:
            raise Exception("Please load a delta before running patch generation")

        # set timestamps in patch object
        patch.base_timestamp = ts_init
        patch.resulting_timestamp = ts_updated

        # get all structural modifications
        s_mods = self.delta.structure_updates

        # loop over structural modifications
        for s_mod in s_mods:
            guid = s_mod.child.attrs["GlobalId"]

            if s_mod.modType == StructuralModificationTypeEnum.ADDED:
                ts = ts_updated
            elif s_mod.modType == StructuralModificationTypeEnum.DELETED:
                ts = ts_init
            else:
                raise Exception("Modification type has not been specified properly. ")

            # generate pushOut Pattern
            cy = """
                   MATCH pa = (n:PrimaryNode:{0} {{GlobalId: \"{1}\"}})-[:rel*..10]->(sec:SecondaryNode:{0})
                   WHERE NOT (sec)-[:EQUIVALENT_TO]-() 
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
                cy_equ_neighbor = "match p = (n)-[r:rel]->(e)-[:EQUIVALENT_TO]-() WHERE ID(n) = {} return e".format(n.id)
                raw_neighbor = connector.run_cypher_statement(cy_equ_neighbor)

                # check if the newly created node has a relationship to another node
                # that is already present in the target graph
                if raw_neighbor != []:
                    context_node = NodeItem.from_neo4j_response(raw_neighbor[0])[0]
                    # get "first visited from"
                    parent_node = self.delta.node_matching_table.get_parent_primaryNode(context_node)

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

            # init transformation
            gluing_pattern.unify_edge_set()
            push_out_pattern.unify_edge_set()
            context_pattern.unify_edge_set()

            rule = TransformationRule(gluing_pattern=gluing_pattern, push_out_pattern=push_out_pattern,
                                      context_pattern=context_pattern, operation_type=s_mod.modType)

            rule.run_cleanup()

            # add dpo to patch object
            patch.operations.append(rule)
        print("[INFO] generate patch: DONE.")
        return patch

    def apply_patch(self, patch: Patch, connector: Neo4jConnector):
        patch.apply(connector=connector)

    def save_patch_to_json(self, patch: Patch):
        """
        saves a given patch into json
        @param patch:
        @return:
        """

        ts_init = patch.base_timestamp
        ts_updated = patch.resulting_timestamp

        print('[INFO] saving patch ... ')
        f = open('Patch_init{}-updt{}.json'.format(ts_init, ts_updated), 'w')
        f.write(jsonpickle.dumps(patch))
        f.close()
        print('[INFO] saving patch: DONE. ')
        # return jsonpickle.encode(self)

    def load_patch_from_json(self, path: str) -> Patch:
        """
        loads a patch from json
        @param path:
        @return:
        """

        # load graph delta
        with open(path) as f:
            content = f.read()

        print("[INFO] loading delta json....")
        result: Patch = jsonpickle.decode(content)
        print("[INFO] loading delta json: DONE.")

        return result


