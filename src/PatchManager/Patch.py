from typing import List

from PatchManager.TransformationRule import TransformationRule
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum
from neo4j_middleware.neo4jConnector import Neo4jConnector


class Patch(object):

    def __init__(self):
        # an ordered list of operations that should mutate an existing graph into the updated version
        self.operations: List[TransformationRule] = []
        # the model, which the patch gets applied to
        self.base_timestamp: str = ""
        # the timestamp the resulting model should carry
        self.resulting_timestamp: str = ""

    def __repr__(self):
        return 'Patch object: No operations: {}'.format(len(self.operations))

    def apply(self, connector: Neo4jConnector):
        """
        applies the patch on a given host graph
        @param connector:
        @return:
        """

        for rule in self.operations:
            if rule.operation_type == StructuralModificationTypeEnum.ADDED:

                # find context and
                # -> use the base timestamp here
                rule.context_pattern.replace_timestamp(self.base_timestamp)

                cy = rule.context_pattern.to_cypher_match()
                print("[INFO] finding context...")
                # print(cy)
                # raw = connector.run_cypher_statement(cy)
                # print(raw)

                # insert push out
                # rule.push_out_pattern.replace_timestamp(self.base_timestamp)
                # ToDo: perhaps using the base timestamp for the new graphlet is not the best decision
                #  to keep the insertion identifiable.
                #  Consider harmonizing labels after successfully gluing everything together
                print("insert push out")
                cy += rule.push_out_pattern.to_cypher_merge()
                # print(cy)
                # raw = connector.run_cypher_statement(cy)
                # print(raw)

                # glue push out and context
                rule.gluing_pattern.replace_timestamp(self.base_timestamp)
                nodes_push = rule.push_out_pattern.get_unified_node_set() + rule.context_pattern.get_unified_node_set()
                cy += rule.gluing_pattern.to_cypher_merge(nodes_push)
                # print("apply glue")
                # print(cy)

                raw = connector.run_cypher_statement(cy)
                # print(raw)

            elif rule.operation_type == StructuralModificationTypeEnum.DELETED:

                # find context
                cy = rule.context_pattern.to_cypher_match()

                # find glue and remove gluing edges
                cy += rule.gluing_pattern.to_cypher_edge_delete()
                # print(cy)
                connector.run_cypher_statement(cy)

                # Pushout pattern is now detached and can be removed
                cy = rule.push_out_pattern.to_cypher_pattern_delete()
                # print(cy)
                connector.run_cypher_statement(cy)

        # finally: update labels of all nodes

    def apply_inverse(self, connector: Neo4jConnector):

        # loop over all transformations
        for r in self.operations:
            # swap transformation type
            if r.operation_type == StructuralModificationTypeEnum.ADDED:
                r.operation_type = StructuralModificationTypeEnum.DELETED
            elif r.operation_type == StructuralModificationTypeEnum.DELETED:
                r.operation_type = StructuralModificationTypeEnum.ADDED

            self.apply(connector=connector)




