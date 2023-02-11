import jsonpatch
import json

from PatchManager.PatchService import PatchService
from PatchManager.PatchService import Patch
from PatchManager.JsonBasedPatch import JsonBasedPatch


class JsonPatchService(PatchService):
    """
    Manages generating, saving, loading and appliying of JSON patches (see RFC 6902)
    """

    def __init__(self):
        self.init_path: str = None
        self.updt_path: str = None
    
    @classmethod
    def from_data(cls, path_init: str, path_updt: str):
        """
        creates a JsonPatchService instance for JSON-based patching
        @param path_init: the filepath to the initial file
        @param path_updt: the filepath to the updated file
        @return: PatchService instance
        """

        inst = cls()
        inst.init_path = path_init
        inst.updt_path = path_updt

        return inst
        
    def generate_patch(self) -> JsonBasedPatch:
        """
        generate a patch from the given data
        @return: the patch representing the operations
        """

        print("[INFO] generating JsonBasedPatch...\n")
        with open(self.init_path) as init_file:
            init_data = json.load(init_file)

        with open(self.updt_path) as updt_file:
            updt_data = json.load(updt_file)

        print("[INFO] Generating done.")
        return JsonBasedPatch(patch=jsonpatch.make_patch(init_data, updt_data))

    def apply_patch(self, patch: JsonBasedPatch, filepath: str):
        """
        apply a jsonpatch object to a dict
        @param filepath: path to the json file that should be patched
        @return: 
        """
        
        print("[INFO] Applying json patch...\n")
        with open(filepath) as f:
            data_to_patch = json.load(f)
        
        patched_data = patch.apply(data_to_patch)

        print("[INFO] Applying done.")
        return patched_data

    def save_patch_to_json(self, patch: JsonBasedPatch, directory=''):
        """
        saves a given patch into json
        @return:
        """

        with open(directory + 'patch.json', 'w') as f:
            json.dump(patch.to_string(), f)

    def load_patch_from_json(self, path: str) -> JsonBasedPatch:
        """
        loads a patch from json
        @param path:
        @return:
        """

        # load graph delta
        with open(path) as f:
            content = f.read()

        # I present: the most ridiculous line of code ever written
        return JsonBasedPatch(jsonpatch.JsonPatch.from_string(content))
