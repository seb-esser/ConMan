from typing import List

from PatchManager.AttributeRule import AttributeRule
from PatchManager.TransformationRule import TransformationRule
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum
from neo4j_middleware.neo4jConnector import Neo4jConnector


class Patch(object):

    def __init__(self):
        # an ordered list of operations that should mutate an existing graph into the updated version
        self.operations: List[TransformationRule] = []
        # attribute changes
        self.attribute_changes: List[AttributeRule] = []
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

        # loop over all structural transformations
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
                # ToDo: implement validation that transformation has been applied successfully.
                # print(raw)

            elif rule.operation_type == StructuralModificationTypeEnum.DELETED:

                cy = rule.push_out_pattern.to_cypher_pattern_delete()
                connector.run_cypher_statement(cy)

            print("[INFO] Adjusting timestamps... ")
            label_from = self.base_timestamp
            label_to = self.resulting_timestamp

            connector.run_cypher_statement("MATCH (n) REMOVE n:{} SET n:{}".format(label_from, label_to))
            print("[INFO] Adjusting timestamps: DONE.")

        # loop over attribute changes
        for rule in self.attribute_changes:
            # find node
            cy = 'MATCH '

            cy += rule.path.to_cypher(path_number=0)
            # set new attribute value
            cy += " SET {}.{} = {}".format(
                rule.path.get_last_node().get_node_identifier(),
                rule.attribute_name,
                rule.updated_value)

            # run statement
            connector.run_cypher_statement(cy)
            # ToDo: implement validation that transformation has been applied successfully.
            #  Consider adding a RETURN to the cypher statement.

    def apply_inverse(self, connector: Neo4jConnector):
        """
        applies the given patch inversely
        @param connector:
        @return:
        """

        # loop over all transformations
        for r in self.operations:
            print("[INFO] inverting patterns ...")
            # swap transformation type
            if r.operation_type == StructuralModificationTypeEnum.ADDED:
                r.operation_type = StructuralModificationTypeEnum.DELETED
            elif r.operation_type == StructuralModificationTypeEnum.DELETED:
                r.operation_type = StructuralModificationTypeEnum.ADDED

        # swap timestamps
        self.base_timestamp, self.resulting_timestamp = self.resulting_timestamp, self.base_timestamp

        for r in self.attribute_changes:
            # swap updated and initial value
            r.updated_value, r.init_value = r.init_value, r.updated_value

        print("[INFO] applying transformation ...")
        self.apply(connector=connector)
        print("[INFO] applying transformation: DONE.")



