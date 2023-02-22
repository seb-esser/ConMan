from typing import List

import jsonpickle

import progressbar
from PatchManager.AttributeRule import AttributeRule
from PatchManager.GraphBasedPatch import GraphBasedPatch
from PatchManager.PatchBundle import PatchBundle
from PatchManager.PatchService import PatchService
from PatchManager.TransformationRule import TransformationRule
from neo4jGraphDiff.Caption.PropertyModification import PropertyModification
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum, StructureModification
from neo4jGraphDiff.GraphDelta import GraphDelta
from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
from neo4j_middleware.ResponseParser.GraphPath import GraphPath
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class GraphPatchService(PatchService):
    """
    manages loading, applying and saving of graph based patches
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def from_existing_delta(cls, delta, connector: Neo4jConnector):
        """
        creates GraphBasedPatchService object from existing delta object without loading any jsons
        @param connector:
        @param delta:
        @return:
        """
        inst = cls()
        inst.delta: GraphDelta = delta
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
        self.delta: GraphDelta = jsonpickle.decode(content)
        print("[INFO] loading delta json: DONE.")

    def generate_patch(self) -> GraphBasedPatch:
        """
        produces a patch from a given delta
        @return: the patch object
        """

        patch = GraphBasedPatch(self.connector)

        try:
            ts_init = self.delta.ts_init
            ts_updated = self.delta.ts_updated
        except:
            raise Exception("Please load a delta before running patch generation")

        # set timestamps in patch object
        patch.base_timestamp = ts_init
        patch.resulting_timestamp = ts_updated

        # get all modifications
        s_mods: List[StructureModification] = self.delta.structure_updates
        p_mods: List[PropertyModification] = self.delta.property_updates

        increment = 100 / (len(s_mods) + 2)
        percent = 0

        # sort s_mods
        removing_mods = [x for x in s_mods if x.modType == StructuralModificationTypeEnum.DELETED]
        inserting_mods = [x for x in s_mods if x.modType == StructuralModificationTypeEnum.ADDED]

        # loop over structural modifications
        for s_mod in removing_mods + inserting_mods:

            # print progressbar
            percent += increment
            progressbar.print_bar(percent)
            # clear cypher
            cy = ''

            if s_mod.modType == StructuralModificationTypeEnum.ADDED:
                ts = ts_updated
            elif s_mod.modType == StructuralModificationTypeEnum.DELETED:
                ts = ts_init
            else:
                raise Exception("Modification type has not been specified properly. ")

            # init patterns
            context_pattern = GraphPattern()
            gluing_pattern = GraphPattern()
            push_out_pattern = GraphPattern()

            # distinguish if a primary or secondary node has been inserted or removed
            if s_mod.child.get_node_type() == "PrimaryNode":

                # get the pushOut Pattern
                guid = s_mod.child.attrs["GlobalId"]
                cy = """
                     MATCH pa = (n:PrimaryNode:{0} {{GlobalId: \"{1}\"}})-[:rel*..10]->(sec:SecondaryNode:{0})
                     WHERE NOT (sec)-[:EQUIVALENT_TO]-() 
                     RETURN pa,  NODES(pa), RELATIONSHIPS(pa)
                     """.format(ts, guid)

                # query pushout
                raw = self.connector.run_cypher_statement(cy)
                # save pushout
                push_out_pattern.paths.extend(GraphPattern.from_neo4j_response(raw).paths)

            # changes in the secondary structure of a rooted entity
            elif s_mod.child.get_node_type() == "SecondaryNode":

                # construct a path from a primaryNode (having a GUID) to the parent
                reference_primary_node = self.delta.node_matching_table.get_parent_primaryNode(s_mod.parent)

                # query anchor path for removed or inserted node.
                # Returns a path that uniquely accesses the last secondary node already existing (i.e. equivalent_to)

                cy = "MATCH {0}, {1}, p = SHORTESTPATH({2}-[:rel*]->{3}) RETURN p, NODES(p), RELATIONSHIPS(p)".format(
                    reference_primary_node.to_cypher(),
                    s_mod.parent.to_cypher(),
                    reference_primary_node.to_cypher(skip_labels=True, skip_attributes=True),
                    # must be given twice as shortest path doenst allow declaration
                    s_mod.parent.to_cypher(skip_labels=True, skip_attributes=True))
                raw = self.connector.run_cypher_statement(cy)

                anchor_pattern: GraphPattern = GraphPattern.from_neo4j_response(raw)
                # the anchor is already a first part of the context necessary to ensure correct insertion
                context_pattern.paths.extend(anchor_pattern.paths)

                # get the pushOut pattern. Here: get_last_node is the parent_node that is has equiv_to edge

                # path_to_parent + glue + pushOut
                cy = \
                    anchor_pattern.to_cypher_match() + \
                    "MATCH {0}-[:rel]->{1} " \
                    "MATCH pa = {1}-[:rel*..10]->(sec:SecondaryNode:{2})  " \
                    "WHERE NOT (sec)-[:EQUIVALENT_TO]-() " \
                    "RETURN pa, NODES(pa), RELATIONSHIPS(pa)".format(
                        anchor_pattern.get_last_node().to_cypher(skip_attributes=True, skip_labels=True),
                        s_mod.child.to_cypher(skip_labels=True),
                        ts)

                # query pushout
                raw = self.connector.run_cypher_statement(cy)
                push_put = GraphPattern.from_neo4j_response(raw)

                # a special case is the moment, where only one leaf node has been added or deleted.
                # Then, the pattern query returns no paths. To solve this situation, the parent node is queried as well
                # such that we can construct a pattern

                # Special attention must be spent in situations where the child node is still used by other resources
                # such that only the edge must be deleted or inserted

                if push_put is not None:
                    # save pushout
                    push_out_pattern.paths.extend(push_put.paths)
                else:

                    # child node is leaf node. Create virtual node to have a pattern
                    cy = anchor_pattern.to_cypher_match()
                    print(cy)

                    # check if s_mod.child is referenced by other structures.
                    # In this case, only the edge has to be removed.

                    virtual_path = GraphPath(
                        [EdgeItem(start_node=s_mod.child, end_node=NodeItem(node_id=-1), rel_id=-1)])

                    push_out_pattern.paths.append(virtual_path)

            # get the glue between parent and child. Because of the unstable GUIDS,
            # we need to differentiate the prim and sec case again...

            if s_mod.child.get_node_type() == "PrimaryNode":
                pass

            elif s_mod.child.get_node_type() == "SecondaryNode":
                # first get the unique path to reach the parent (secondary) node
                cy_anchor_path = context_pattern.to_cypher_match()
                # secondly, get the edge connecting both and just store the edge in the gluing pattern
                # (the anchor is context!)
                cy = cy_anchor_path + " MATCH p = {}-[:rel]->{} RETURN p, NODES(p), RELATIONSHIPS(p)".format(
                    context_pattern.get_last_node().to_cypher(skip_labels=True, skip_attributes=True),
                    s_mod.child.to_cypher())
                raw = self.connector.run_cypher_statement(cy)
                glue: GraphPattern = GraphPattern.from_neo4j_response(raw)

                if glue is None:
                    print("got none pattern")
                gluing_pattern.paths.extend(glue.paths)

            # calculate the gluing for prim and secondary
            # finally, calculate all gluing edges between pushout nodes and context
            nodes_pushed_out = push_out_pattern.get_unified_node_set()

            # calculate all embedding edges for the pushout pattern
            for n in nodes_pushed_out:
                cy_equ_neighbor = "match p = (n)-[r:rel]->(e)-[:EQUIVALENT_TO]-() WHERE ID(n) = {} return e".format(
                    n.id)
                raw_neighbor = self.connector.run_cypher_statement(cy_equ_neighbor)

                # check if the newly created node has a relationship to another node
                # that is already present in the target graph
                if raw_neighbor != []:
                    context_node = NodeItem.from_neo4j_response(raw_neighbor[0])[0]
                    # get "first visited from" for the context_node
                    parent_node = self.delta.node_matching_table.get_parent_primaryNode(context_node)

                    # calculate the unique path describing the context node
                    cy = "MATCH {0}, {1}, p = SHORTESTPATH({2}-[:rel*]->{3}) " \
                         "RETURN p, NODES(p), RELATIONSHIPS(p)".format(
                            parent_node.to_cypher(),
                            context_node.to_cypher(),
                            parent_node.to_cypher(skip_labels=True, skip_attributes=True),
                            context_node.to_cypher(skip_labels=True, skip_attributes=True))
                    raw = self.connector.run_cypher_statement(cy)
                    embed: GraphPattern = GraphPattern.from_neo4j_response(raw)
                    context_pattern.paths.append(embed.paths[0])

                    # calculate the gluing edge connecting embed and push out
                    cy = "MATCH p = {}-[r:rel]->{} RETURN p, NODES(p), RELATIONSHIPS(p)".format(
                        n.to_cypher(skip_attributes=False, skip_labels=False),
                        context_node.to_cypher(skip_attributes=False, skip_labels=False))
                    raw = self.connector.run_cypher_statement(cy)
                    glue: GraphPattern = GraphPattern.from_neo4j_response(raw)

                    # add gluing edge
                    gluing_pattern.paths.append(glue.paths[0])

            if not len(gluing_pattern.paths) > 0:
                Warning("graph pattern must not have zero paths")

            if not len(push_out_pattern.paths) > 0:
                Warning("graph pattern must not have zero paths")

            if not len(context_pattern.paths) != 0:
                Warning("graph pattern must not have zero paths")

            # init transformation
            gluing_pattern.unify_edge_set()
            push_out_pattern.unify_edge_set()
            context_pattern.unify_edge_set()

            # verify that patterns are not empty
            for path in push_out_pattern.paths:
                if len(path.segments) == 0:
                    raise Exception("something seems wrong with the patterns at question. ")

            rule = TransformationRule(gluing_pattern=gluing_pattern, push_out_pattern=push_out_pattern,
                                      context_pattern=context_pattern, operation_type=s_mod.modType)

            # rule.run_cleanup()

            # add dpo to patch object
            patch.operations.append(rule)

        # loop over all p_mods
        for p_mod in p_mods:
            path = p_mod.pattern.paths[0]
            attr_name = p_mod.attrName
            init_val = p_mod.valueOld
            updt_val = p_mod.valueNew
            rule = AttributeRule(path=path, attribute_name=attr_name, init_value=init_val, updated_value=updt_val)
            patch.attribute_changes.append(rule)

            # store connectionNode structures

        pushout_init, context_init, glue_init = self.__extract_conNode_patterns(self.connector, ts=ts_init)
        pushout_updt, context_updt, glue_updt = self.__extract_conNode_patterns(self.connector, ts=ts_updated)

        remove_rule = TransformationRule(gluing_pattern=glue_init,
                                         push_out_pattern=pushout_init,
                                         context_pattern=context_init,
                                         operation_type=StructuralModificationTypeEnum.DELETED)

        insert_rule = TransformationRule(gluing_pattern=glue_updt,
                                         push_out_pattern=pushout_updt,
                                         context_pattern=context_updt,
                                         operation_type=StructuralModificationTypeEnum.ADDED)

        percent += increment
        progressbar.print_bar(percent)
        patch.operations.append(remove_rule)

        percent += increment
        progressbar.print_bar(percent)
        patch.operations.append(insert_rule)

        return patch

    def apply_patch(self, patch: GraphBasedPatch):
        patch.apply_version2()

    def apply_patch_inverse(self, patch: GraphBasedPatch):
        patch.apply_inverse()

    def save_patch_to_json(self, patch: GraphBasedPatch, directory=''):
        """
        saves a given patch into json
        @param patch:
        @return:
        """

        ts_init = patch.base_timestamp
        ts_updated = patch.resulting_timestamp

        print('[INFO] Saving patch ... ')
        f = open(directory + 'Patch_init{}-updt{}.json'.format(ts_init, ts_updated), 'w')
        f.write(jsonpickle.dumps(patch))
        f.close()

        # return jsonpickle.encode(self)

    def load_patch_from_json(self, path: str) -> GraphBasedPatch:
        """
        loads a patch from json
        @param path:
        @return:
        """

        # load graph delta
        with open(path) as f:
            content = f.read()

        result: GraphBasedPatch = jsonpickle.decode(content)

        return result

    def save_patch_bundle_to_json(self, patch_bundle: PatchBundle):
        """
                saves a given patch bundle into json
                @param patch_bundle:
                """

        commit_hash = hash(patch_bundle)

        print('[INFO] Saving patch bundle {} '.format(commit_hash))
        f = open('PatchBundle_{}.json'.format(commit_hash), 'w')
        f.write(jsonpickle.dumps(patch_bundle))
        f.close()

    def load_patch_bundle_from_json(self, path: str) -> PatchBundle:
        """
        loads a patch bundle from json
        @param path:
        @return:
        """

        # load graph delta
        with open(path) as f:
            content = f.read()

        result: PatchBundle = jsonpickle.decode(content)

        return result

    def __extract_conNode_patterns(self, connector: Neo4jConnector, ts: str):
        """

        @param connector:
        @param con_node_pattern:
        @param ts:
        @return:
        """
        all_glue = GraphPattern()
        all_context = GraphPattern()

        # pushout
        cy = "MATCH p = (c:ConnectionNode:{0}) RETURN p, NODES(p), RELATIONSHIPS(p)".format(ts)
        push_out: GraphPattern = GraphPattern.from_neo4j_response(connector.run_cypher_statement(cy))

        # calculate glue and context
        for path in push_out.paths:
            cy = "MATCH p = {0}-[:rel]->(n:{1})  " \
                 "RETURN p, NODES(p), RELATIONSHIPS(p)".format(path.get_start_node().to_cypher(), ts)
            raw = connector.run_cypher_statement(cy)
            glue = GraphPattern.from_neo4j_response(raw)
            # remove glues to materials for the moment -> to be issued
            paths_to_prim_or_ownerHist = [x for x in glue.paths
                                          if x.segments[0].end_node.get_entity_type() == "IfcOwnerHistory"
                                          or x.segments[0].end_node.get_node_type() == "PrimaryNode"]
            all_glue.paths.extend(paths_to_prim_or_ownerHist)

            # get context for those gluing edges that have not been sorted out
            for glue_target in [x.segments[0].end_node for x in paths_to_prim_or_ownerHist]:

                if glue_target.get_node_type() == "SecondaryNode":

                    if glue_target.get_entity_type() == "IfcOwnerHistory":
                        # query context
                        cy = "MATCH p = SHORTESTPATH({0}<-[:rel*]-(n:PrimaryNode:{1}{{EntityType: \"IfcProject\"}})) " \
                             "RETURN p, NODES(p), RELATIONSHIPS(p)".format(glue_target.to_cypher(), ts)
                        raw = connector.run_cypher_statement(cy)
                        context_current_node = GraphPattern.from_neo4j_response(raw)

                        # if context_current_node.paths[0] not in context_init.paths:

                        all_context.paths.append(context_current_node.paths[0])

                    else:
                        print(Warning("These gluing cases are not yet supported. Target: {}"
                                      "".format(glue_target.get_entity_type())))
                        continue

                elif glue_target.get_node_type() == "PrimaryNode":
                    # glue target has guid
                    path_to_current_node = GraphPath(segments=[
                        EdgeItem(start_node=glue_target, end_node=NodeItem(-1), rel_id=-1)
                    ]
                    )
                    # if path_to_current_node not in context_init.paths:
                    all_context.paths.append(path_to_current_node)

        return push_out, all_context, all_glue
