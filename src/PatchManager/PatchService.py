
from PatchManager.Patch import Patch

class PatchService():
    
    @classmethod
    def from_data(cls):
        pass

    def generate_patch(self):
        pass

    def apply_patch(self, patch: Patch):
        pass

    def save_patch_to_json(self, patch: Patch, directory: str=''):
        pass

    def load_patch_from_json(self, path: str):
        pass