from jsonpatch import JsonPatch

from PatchManager.Patch import Patch

class JsonBasedPatch(Patch):

    def __init__(self, patch: JsonPatch):
        self.patch: JsonPatch = patch

    def to_string(self) -> str:
        return self.patch.to_string()
    
    def apply(self, dict_to_patch: dict) -> dict:
        """
        intermediary apply method for oop
        """
        return self.patch.apply(dict_to_patch)
