from typing import List
import re

from PatchManager.AttributeRule import AttributeRule
from PatchManager.TransformationRule import TransformationRule
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
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

        print("Applying attribute changes... ")
        # loop over attribute changes
        for rule in self.attribute_changes:
            # find node
            cy = 'MATCH '

            cy += rule.path.to_cypher(path_number=0)
            # set new attribute value
            if isinstance(rule.updated_value, str) or rule.updated_value is None:
                cy += " SET {}.{} = \"{}\"".format(
                    rule.path.get_last_node().get_node_identifier(),
                    rule.attribute_name,
                    rule.updated_value)
            else:
                cy += " SET {}.{} = {}".format(
                    rule.path.get_last_node().get_node_identifier(),
                    rule.attribute_name,
                    rule.updated_value)

            # run statement
            connector.run_cypher_statement(cy)
            # ToDo: implement validation that transformation has been applied successfully.
            #  Consider adding a RETURN to the cypher statement.

        print("Applying structural changes... ")
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

                # prevent pattern statement to declare nodes and edges more than once
                n = rule.context_pattern.get_unified_node_set()
                e = rule.context_pattern.get_unified_edge_set()

                cy += rule.push_out_pattern.to_cypher_merge(n, e)
                self.hightlight_patch(rule, connector)
                # print(cy)
                # raw = connector.run_cypher_statement(cy)
                # print(raw)

                # glue push out and context
                rule.gluing_pattern.replace_timestamp(self.base_timestamp)

                # prevent cypher query contain node and edge definitions more than once
                nodes_push = rule.push_out_pattern.get_unified_node_set() + rule.context_pattern.get_unified_node_set()
                edges_push = rule.push_out_pattern.get_unified_edge_set() + rule.context_pattern.get_unified_edge_set()

                cy += rule.gluing_pattern.to_cypher_merge(nodes_push, edges_push)
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
            r.path.segments[-1].end_node.attrs[r.attribute_name] = r.updated_value

        print("[INFO] applying transformation ...")
        self.apply(connector=connector)
        print("[INFO] applying transformation: DONE.")


    def hightlight_patch(self, rule: TransformationRule, connector: Neo4jConnector):
        """
        applies a new label to the push_out_pattern of a given rule
        @param rule: The TransformationRule in question
        @param connector: Neo4jConnector instance
        @return: None
        """
        # gett all nodes of the pattern
        push_out_nodes: List[NodeItem] = rule.push_out_pattern.get_unified_node_set()

        cy = ""
        # for all NodeItems except the last
        for node in push_out_nodes:
            # replace the "nXXX" with just "n"
            new_match = re.sub('n[0-9]+:', 'n:', node.to_cypher())
            # if the NodeItem isn't the last, add a UNION to execute everything in one db call
            if node != push_out_nodes[-1]:
                union = "UNION "
            else:
                union = ""
            # Set the label according to the ModificytionType 
            if rule.operation_type == StructuralModificationTypeEnum.ADDED:
                cy += "MATCH" + new_match + " SET n:Added " + union
            elif rule.operation_type == StructuralModificationTypeEnum.DELETED:
                cy += "MATCH" + new_match + " SET n:Deleted " + union
        
        # run the cypher statement
        connector.run_cypher_statement(cy)



