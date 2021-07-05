from PatchManager.Operation.AttributeOperations.AddAttributeOperation import AddAttributeOperation
from PatchManager.Operation.AttributeOperations.DeleteAttributeOperation import DeleteAttributeOperation
from PatchManager.Operation.AttributeOperations.ModifyAttributeOperation import ModifyAttributeOperation
from PatchManager.Operation.PatternOperations.AddPatternOperation import AddPatternOperation
from PatchManager.Operation.PatternOperations.RemovePatternOperation import RemovePatternOperation
from PatchManager.Patch import Patch
from neo4jGraphDiff.Caption.PropertyModification import PropertyModificationTypeEnum
from neo4jGraphDiff.Caption.ResultGenerator import ResultGenerator
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.neo4jConnector import Neo4jConnector

import json


class PatchGenerator:

    def __init__(self, connector: Neo4jConnector):
        self.patch = Patch()
        self.connector: Neo4jConnector = connector

    def __repr__(self):
        return 'Patch generator translating a given DiffResult object into a patch object'

    def get_patch(self) -> Patch:
        """
        returns the generated patch object
        @return: patch object
        """
        return self.patch

    def create_patch_from_graph_diff(self, res: ResultGenerator):
        """
        creates a patch from a given SubstructureDiffResult object.
        The SubstructureDiffResult is achieved by running the DfsIsomorphismCalculator
        @param res:
        """

        # set time stamps
        self.patch.base_timestamp = res.timestamp_init
        self.patch.resulting_timestamp = res.timestamp_updated
        self.patch.ignore_attrs = res.config.DiffSettings.diffIgnoreAttrs


        # --- connection node Updates ---
        # ToDo: implement suitable approaches to capture connectionNode insertions and deletions

        # --- Primary Node Updates ---
        added_primary_nodes = res.ResultPrimaryDiff['added']
        deleted_primary_nodes = res.ResultPrimaryDiff['deleted']

        for added_node in added_primary_nodes:

            # query position in primary structure
            cy = Neo4jQueryFactory.get_parent_connection_node(added_node.id)
            raw_res = self.connector.run_cypher_statement(cy)
            sub_pattern = GraphPattern.from_neo4j_response(raw_res)
            sub_pattern.load_rel_attrs(self.connector)

            # create instance of addPatternOperation

            ref_node = sub_pattern.get_entry_node()
            ref_node.tidy_attrs()
            reference_structure = ref_node.to_cypher(node_identifier='c', include_nodeType_label=True)

            print('MATCH {} RETURN c'.format(reference_structure) )
            add_pattern = sub_pattern.to_cypher_create()

            add_pattern_op = AddPatternOperation(pattern=add_pattern,
                                                 reference_structure=reference_structure,
                                                 prim_guid=ref_node.attrs['GlobalId'])

            self.patch.operations.append(add_pattern_op)

        for deleted_node in deleted_primary_nodes:
            # query substructure from this node
            cy = Neo4jQueryFactory.get_distinct_paths_from_node(deleted_node.id)
            raw_res = self.connector.run_cypher_statement(cy)
            sub_pattern = GraphPattern.from_neo4j_response(raw_res)

            # create instance of addPatternOperation
            add_pattern_op = RemovePatternOperation(pattern=sub_pattern)
            self.patch.pattern_operations.append(add_pattern_op)

        # --- Secondary modifications ---

        for mod in res.ResultComponentDiff:
            property_mods = mod.propertyModifications
            strucural_mods = mod.StructureModifications

            # Secondary: property modifications
            for p in property_mods:
                pattern: GraphPattern = p.pattern
                pattern.load_rel_attrs(connector=self.connector)
                entry_node = pattern.get_entry_node()
                primary_node_guid = entry_node.attrs['GlobalId']

                if p.modificationType == PropertyModificationTypeEnum.ADDED:

                    operation = AddAttributeOperation(prim_guid=primary_node_guid,
                                                      pattern=pattern,
                                                      attrName=p.attrName,
                                                      attrValNew=p.valueNew)

                elif p.modificationType == PropertyModificationTypeEnum.DELETED:
                    operation = DeleteAttributeOperation(prim_guid=primary_node_guid,
                                                         pattern=pattern,
                                                         attrName=p.attrName,
                                                         attrValOld=p.valueOld)

                elif p.modificationType == PropertyModificationTypeEnum.MODIFIED:
                    operation = ModifyAttributeOperation(prim_guid=primary_node_guid,
                                                         pattern=pattern,
                                                         attrName=p.attrName,
                                                         attrValOld=p.valueOld,
                                                         attrValNew=p.valueNew)
                else:
                    raise Exception("unhandled modification type occurred")
                # assign operation to patch
                self.patch.operations.append(operation)

            # Secondary: structural modifications
            for s in strucural_mods:
                pass
                # print(s)

        return self.patch

    def export_to_json(self):
        """
        returns a json object
        @return:
        """
        return self.patch.to_json()
