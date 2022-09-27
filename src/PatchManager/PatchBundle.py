from typing import List

from PatchManager.Patch import Patch
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
        for patch in self.patches:
            patch.apply(connector=connector)
