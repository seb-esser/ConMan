from PatchManager.Operation.AttributeOperations.AddAttributeOperation import AddAttributeOperation
from PatchManager.Operation.AttributeOperations.DeleteAttributeOperation import DeleteAttributeOperation
from PatchManager.Operation.AttributeOperations.ModifyAttributeOperation import ModifyAttributeOperation
from PatchManager.Patch import Patch
from neo4jGraphDiff.Caption.ResultGenerator import ResultGenerator
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult, PropertyModificationTypeEnum
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector

import json


class PatchGenerator:

    def __init__(self, connector: Neo4jConnector):
        self.patch= Patch()
        self.connector: Neo4jConnector = connector

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

        # --- Secondary structure modifications ---
        for p_mod in res.ResultComponentDiff:
            struc_mods = p_mod.StructureModifications
            prop_mods = p_mod.propertyModifications

            for p in prop_mods:
                mutation = {}
                root_init = p.nodeId_init
                root_updated = p.nodeId_updated

                # calc hashsum
                cy = Neo4jQueryFactory.get_hash_by_nodeId(res.timestamp_init, root_init, self.patch.ignore_attrs)
                hashsum = self.connector.run_cypher_statement(cy, 'hash_value')[0]

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


        # --- Structural modifications ---

    def to_json(self):
        return json.dump(self)
