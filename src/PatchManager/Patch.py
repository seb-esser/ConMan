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

                # find context
                cy = rule.context_pattern.to_cypher_match()
                # connector.run_cypher_statement(cy)
                # print(cy)

                # insert push out
                cy = rule.push_out_pattern.to_cypher_merge()

                # glue push out and context
                cy = rule.gluing_pattern.to_cypher_merge()

            elif rule.operation_type == StructuralModificationTypeEnum.DELETED:
                # find push out
                cy = rule.push_out_pattern.to_cypher_match()

                # detach and remove

        # finally: update labels of all nodes


