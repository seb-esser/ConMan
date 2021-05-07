from PatchManager.Operation import AbstractOperation
import jsonpickle


class Patch(object):

    def __init__(self):
        # an ordered list of operations that should mutate an existing graph into the updated version
        self.operations: list[AbstractOperation] = []
        # the model, which the patch gets applied to
        self.base_timestamp: str = ""
        # the timestamp the resulting model should carry
        self.resulting_timestamp: str = ""

    def __repr__(self):
        return 'Patch object'

    def to_json(self):
        return jsonpickle.encode(self)





