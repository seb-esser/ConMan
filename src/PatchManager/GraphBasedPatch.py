from typing import List
import re

from PatchManager.AttributeRule import AttributeRule
from PatchManager.TransformationRule import TransformationRule
from PatchManager.Patch import Patch
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector
import progressbar


class GraphBasedPatch(Patch):

    def __init__(self, connector: Neo4jConnector):
        # an ordered list of operations that should mutate an existing graph into the updated version
        self.operations: List[TransformationRule] = []
        # attribute changes
        self.attribute_changes: List[AttributeRule] = []
        # the model, which the patch gets applied to
        self.base_timestamp: str = ""
        # the timestamp the resulting model should carry
        self.resulting_timestamp: str = ""
        # Neo4jConnector instance
        self.connector = connector

    def __repr__(self):
        return 'Patch object: No operations: {}'.format(len(self.operations))

    def apply(self):
        """
        applies the patch on a given host graph
        @return:
        """

        print("Applying semantic transformations... ")
        # loop over attribute changes
        for rule in self.attribute_changes:
            self.__apply_attribute_rule(rule)

        print("Applying topological transformations ... ")
        # loop over all structural transformations
        for rule in self.operations:
            if rule.operation_type == StructuralModificationTypeEnum.ADDED:

                # find context and
                # -> use the base timestamp here
                if len(rule.context_pattern.paths) < 0:  # catch situation in which no context exists in the rule
                    rule.context_pattern.replace_timestamp(self.base_timestamp)

                cy = rule.context_pattern.to_cypher_match()
                print("[INFO] finding context...")
                # print(cy)
                # raw = self.connector.run_cypher_statement(cy)
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
                # self.highlight_patch(self.connector)
                # print(cy)
                # raw = self.connector.run_cypher_statement(cy)
                # print(raw)

                # glue push out and context
                if len(rule.gluing_pattern.paths) < 0:
                    rule.gluing_pattern.replace_timestamp(self.base_timestamp)

                # prevent cypher query contain node and edge definitions more than once
                nodes_push = rule.push_out_pattern.get_unified_node_set() + rule.context_pattern.get_unified_node_set()
                edges_push = rule.push_out_pattern.get_unified_edge_set() + rule.context_pattern.get_unified_edge_set()

                cy += rule.gluing_pattern.to_cypher_merge(nodes_push, edges_push)
                # print("apply glue")
                # print(cy)

                raw = self.connector.run_cypher_statement(cy)
                # ToDo: implement validation that transformation has been applied successfully.
                # print(raw)

            elif rule.operation_type == StructuralModificationTypeEnum.DELETED:

                cy = rule.push_out_pattern.to_cypher_pattern_delete()
                self.connector.run_cypher_statement(cy)

            # print("[INFO] Adjusting timestamps... ")
            label_from = self.base_timestamp
            label_to = self.resulting_timestamp

            self.connector.run_cypher_statement("MATCH (n:{0}) REMOVE n:{0} SET n:{1}".format(label_from, label_to))
            # print("[INFO] Adjusting timestamps: DONE.")

    def apply_version2(self):

        inserting_rules = [x for x in self.operations if x.operation_type == StructuralModificationTypeEnum.ADDED]
        removing_rules = [x for x in self.operations if x.operation_type == StructuralModificationTypeEnum.DELETED]
        print("Applying removal rules... ")
        # removing stuff

        increment = 100 / (len(inserting_rules) + len(removing_rules) + len(self.attribute_changes))
        percent = 0
        for rule in removing_rules:
            # print progressbar
            percent += increment
            progressbar.print_bar(percent)
            context = rule.context_pattern
            glue = rule.gluing_pattern

            # context should be found in the initial (i.e. host) graph
            context.replace_timestamp(self.base_timestamp)
            context.tidy_node_attributes()
            context.remove_OwnerHistory_links()

            # match context, glue and pushout first
            search = GraphPattern()
            search.paths.extend(rule.context_pattern.paths)
            search.paths.extend(rule.gluing_pattern.paths)
            search.paths.extend(rule.push_out_pattern.paths)
            cy = search.to_cypher_match(define_return=False)

            # delete the gluing and pushout edges
            for edge in glue.paths + rule.push_out_pattern.paths:
                if edge.segments[0].is_virtual_edge():
                    continue
                cy += "DELETE e{} ".format(edge.segments[0].edge_id)

            # ToDo
            # run the node delete operation of the pushout part.
            # ignore nodes that are part of the context pattern
            context_nodes = rule.context_pattern.get_unified_node_set()
            cy += rule.push_out_pattern.to_cypher_node_delete(include_detach=True, ignore_nodes=context_nodes)
            print(cy)

            self.connector.run_cypher_statement(cy)

        print("Applying attribute changes... ")
        # loop over attribute changes
        for rule in self.attribute_changes:
            percent += increment
            progressbar.print_bar(percent)
            
            self.__apply_attribute_rule(rule)

        print("Applying insertion rules... ")

        print("updating timestamps 1/2")
        label_from = self.base_timestamp
        label_to = self.resulting_timestamp

        self.connector.run_cypher_statement("MATCH (n:{0}) SET n:{1}".format(label_from, label_to))

        for rule in inserting_rules:

            if rule is inserting_rules[-1]:
                print("applying conNode edges...")
                # ToDo: Run with relaxed semantic conditions in the match statements - seems like there is an issue

            if rule.context_pattern.is_empty() or rule.gluing_pattern.is_empty():
                continue

            # rule.context_pattern.replace_timestamp(self.base_timestamp)
            # find context pattern
            cy = rule.context_pattern.to_cypher_match(optional_match=False, entType_guid_only=True)

            # create push-out
            cy += rule.push_out_pattern.to_cypher_merge()

            # this node is part of the pushout but can be addressed by it p21 id and the timestamp for the moment
            start_nodes = rule.push_out_pattern.get_unified_node_set() + rule.context_pattern.get_unified_node_set()
            for p in rule.gluing_pattern.paths:
                glue_start = p.segments[0].start_node

                if glue_start in rule.push_out_pattern.get_unified_node_set():
                    # node already specified, no need to re-specify
                    continue

                if glue_start not in start_nodes:

                    if glue_start in rule.context_pattern.get_unified_node_set():
                        # node has been already declared, use reduced cy representation
                        cy += "MATCH " + glue_start.to_cypher(skip_attributes=True, skip_labels=True)
                    else:
                        start_nodes.append(glue_start)
                        cy += "MATCH " + glue_start.to_cypher()

            nodes_context = rule.context_pattern.get_unified_node_set()
            cy += rule.gluing_pattern.to_cypher_merge(nodes_specified=[*start_nodes, *nodes_context], edges_specified=[])
            print(cy)
            self.connector.run_cypher_statement(cy)


        # harmonize labels
        label_from = self.base_timestamp
        label_to = self.resulting_timestamp
        print("updating timestamps 2/2")
        self.connector.run_cypher_statement("MATCH (n:{0}) REMOVE n:{0} SET n:{1}".format(label_from, label_to))

    def apply_inverse(self):
        """
        applies the given patch inversely
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
        self.apply()
        print("[INFO] applying transformation: DONE.")

    def highlight_patch(self):
        """
        applies a new label to the push_out_pattern of
        @return: None
        """

        # highlight removed and inserted nodes
        for rule in self.operations:
            # get all nodes of the pattern
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
                # Set the label according to the ModificationType
                if rule.operation_type == StructuralModificationTypeEnum.ADDED:
                    cy += "MATCH" + new_match + " SET n:ADDED " + union
                elif rule.operation_type == StructuralModificationTypeEnum.DELETED:
                    cy += "MATCH" + new_match + " SET n:DELETED " + union

            # run the cypher statement
            self.connector.run_cypher_statement(cy)

        # highlight modified nodes
        for pMod in self.attribute_changes:
            # remove p21_id etc from nodes
            pMod.path.tidy_node_attributes()
            pMod.path.segments[-1].end_node.attrs = {}

            cy = "MATCH "
            cy += pMod.path.to_cypher(skip_timestamp=True)

            cy += "SET {}:MODIFIED".format(pMod.path.get_last_node().get_node_identifier())
            self.connector.run_cypher_statement(cy)

    def remove_highlight_labels(self):

        cy = "MATCH (n:ADDED), (m:DELETED), (o:MODIFIED) " \
             "REMOVE n:ADDED, m:DELETED, o:MODIFIED"
        self.connector.run_cypher_statement(cy)

    def __apply_attribute_rule(self, rule):
        """

        """
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
        self.connector.run_cypher_statement(cy)
