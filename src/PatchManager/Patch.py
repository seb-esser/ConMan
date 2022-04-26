from typing import List

import jsonpickle

from PatchManager.TransformationRule import TransformationRule
from neo4jGraphDiff.Caption.StructureModification import StructuralModificationTypeEnum


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

    def to_json(self):
        return jsonpickle.encode(self)
    # ToDo: call to_json for each dpo-rule

    def apply(self, ts_host: str):
        """
        applies the patch on a given host graph
        @param ts_host:
        @return:
        """

        for rule in self.operations:


            # find context
            cy = rule.context_pattern.to_cypher_match()
            print(cy)

            #


from typing import List

import jsonpickle

from PatchManager.TransformationRule import TransformationRule


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

    def to_json(self):

        print('[INFO] saving patch ... ')
        f = open('Patch_init{}-updt{}.json'.format(self.base_timestamp, self.resulting_timestamp), 'w')
        f.write(jsonpickle.dumps(self))
        f.close()
        print('[INFO] saving patch: DONE. ')
        # return jsonpickle.encode(self)

    @classmethod
    def from_json(cls, path: str):
        print('[INFO] opening patch ... ')
        f = open(path, 'w')
        raw = jsonpickle.decode(f.read())
        f.close()

        print('[INFO] opening patch: DONE. ')
        return cls(f)
        # todo: implement proper de and encoding

    def apply(self, ts_host: str):
        """
        applies the patch on a given host graph
        @param ts_host:
        @return:
        """

        for rule in self.operations:

            if rule.operation_type == StructuralModificationTypeEnum.ADDED:

                # find context
                cy = rule.context_pattern.to_cypher_match()
                print(cy)

                # insert push out
                cy = rule.push_out_pattern.to_cypher_merge()

                # glue push out and context
                cy = rule.gluing_pattern.to_cypher_merge()

            elif rule.operation_type == StructuralModificationTypeEnum.DELETED:
                # find push out
                cy = rule.push_out_pattern.to_cypher_match()

                # detach and remove

        # finally: update labels of all nodes


