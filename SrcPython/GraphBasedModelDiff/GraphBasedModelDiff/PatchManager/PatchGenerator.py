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


        # --- Primary Node Updates ---
        added = res.ResultPrimaryDiff['added']
        deleted = res.ResultPrimaryDiff['deleted']

        for added_node in added:

            # query substructure from this node
            cy = Neo4jQueryFactory.get_distinct_paths_from_node(added_node.id)
            raw_res = self.connector.run_cypher_statement(cy)
            sub_pattern = GraphPattern.from_neo4j_response(raw_res)
            sub_pattern.load_rel_attrs(self.connector)

            # create instance of addPatternOperation
            add_pattern_op = AddPatternOperation(pattern=sub_pattern)
            self.patch.operations.append(add_pattern_op)

        for deleted_node in deleted:
            # query substructure from this node
            cy = Neo4jQueryFactory.get_distinct_paths_from_node(deleted_node.id)
            raw_res = self.connector.run_cypher_statement(cy)
            sub_pattern = GraphPattern.from_neo4j_response(raw_res)

            # create instance of addPatternOperation
            add_pattern_op = RemovePatternOperation(pattern=sub_pattern)
            self.patch.pattern_operations.append(add_pattern_op)

        # --- Secondary modifications ---

        for p_mod in res.ResultComponentDiff:
            prop_mods = p_mod.propertyModifications
            struc_mods = p_mod.StructureModifications

            # Secondary: property modifications
            for p in prop_mods:
                mutation = {}
                root_init = p.nodeId_init
                root_updated = p.nodeId_updated

                # calc hashsum
                cy = Neo4jQueryFactory.get_hash_by_nodeId(res.timestamp_init, root_init, self.patch.ignore_attrs)
                hashsum = self.connector.run_cypher_statement(cy, 'hash')[0]

                if p.modificationType == PropertyModificationTypeEnum.ADDED:
                    operation = AddAttributeOperation(prim_hash=hashsum,
                                                      pattern=p.path_init.to_patch(),
                                                      attrName=p.attrName,
                                                      attrValNew=p.valueNew)

                elif p.modificationType == PropertyModificationTypeEnum.DELETED:
                    operation = DeleteAttributeOperation(prim_hash=hashsum,
                                                         pattern=p.path_init.to_patch(),
                                                         attrName=p.attrName,
                                                         attrValOld=p.valueOld)

                elif p.modificationType == PropertyModificationTypeEnum.MODIFIED:
                    operation = ModifyAttributeOperation(prim_hash=hashsum,
                                                         pattern=p.path_init.to_patch(),
                                                         attrName=p.attrName,
                                                         attrValOld=p.valueOld,
                                                         attrValNew=p.valueNew
                                                         )
                else:
                    raise Exception("unhandled modification type occured")
                # assign operation to patch
                self.patch.operations.append(operation)

            # Secondary: structural modifications
            for s in struc_mods:
                raise NotImplementedError('Structural modifications on secondary nodes are not captured yet. ')

        return self.patch

    def export_to_json(self):
        return self.patch.to_json()
