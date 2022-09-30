import jsonpickle
import requests

from PatchManager.PatchBundle import PatchBundle
from PatchManager.PatchService import PatchService


def push():
    base_url = "http://localhost:5000"
    endpoint = "/conman/push"

    api_location = base_url + endpoint

    # get patch bundle
    path = 'PatchBundle_{}.json'.format(121891797032)
    patch_bundle = PatchService().load_patch_from_json(path=path)

    # post bundle on server

    res = requests.post(api_location, json=jsonpickle.encode(patch_bundle))
    print("pushed patch with message > {} < to remote. ".format(patch_bundle.message))


if __name__ == "__main__":
    push()
