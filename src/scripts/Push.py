import jsonpickle
import requests

from PatchManager.PatchBundle import PatchBundle


def push():
    base_url = "http://localhost:5000"
    endpoint = "/conman/push"

    api_location = base_url + endpoint

    # get patch bundle
    # ToDo: Replace DummyBundle with real bundles
    patch_bundle = PatchBundle("test1")

    # post bundle on server

    res = requests.post(api_location, json=jsonpickle.encode(patch_bundle))
    print(res.content)


if __name__ == "__main__":
    push()
