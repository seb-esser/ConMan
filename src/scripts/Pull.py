import jsonpickle
import requests

from PatchManager.PatchBundle import PatchBundle
from neo4j_middleware.neo4jConnector import Neo4jConnector


def pull():

    # load latest patchBundle from server
    base_url = "http://localhost:5000"
    endpoint = "/conman/pull"

    api_location = base_url + endpoint

    res = requests.get(api_location)
    patch_bundle: PatchBundle = jsonpickle.decode(res.content)

    # apply patch_bundle
    connector = Neo4jConnector()
    connector.connect_driver()

    patch_bundle.apply(connector=connector)

    connector.disconnect_driver()


if __name__ == "__main__":
    pull()
