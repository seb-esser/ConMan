from typing import List

from PatchManager.Patch import Patch
from neo4j_middleware.BucketManager.BucketUtility import BucketUtility
from neo4j_middleware.neo4jConnector import Neo4jConnector


class PatchBundle:

    def __init__(self, message):
        """
        constructor for patchBundle
        @param message: commit message
        """
        self.patches: List[Patch] = []
        self.message = message

    def apply(self, connector: Neo4jConnector):
        """
        applies all transformations in the bundle
        """

        bucket_util = BucketUtility()

        for patch in self.patches:
            if bucket_util.bool_timestamp_exists(patch.base_timestamp):
                patch.apply(connector=connector)
            else:
                print("skipping patch because no host graph with suitable base timestamp has been detected. ")
