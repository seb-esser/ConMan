from typing import List

from PatchManager.DoublePushOut import DoublePushOut
from PatchManager.Operation import AbstractOperation
import jsonpickle

from neo4jGraphDiff.Caption.NodeMatchingTable import NodeMatchingTable


class Patch(object):

    def __init__(self):
        # an ordered list of operations that should mutate an existing graph into the updated version
        self.operations: List[DoublePushOut] = []
        # the model, which the patch gets applied to
        self.base_timestamp: str = ""
        # the timestamp the resulting model should carry
        self.resulting_timestamp: str = ""

    def __repr__(self):
        return 'Patch object: No operations: {}'.format(len(self.operations))

    def to_json(self):
        return jsonpickle.encode(self)
    # ToDo: call to_json for each dpo-rule



