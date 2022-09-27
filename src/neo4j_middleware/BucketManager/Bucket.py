from datetime import datetime
from typing import List

from neo4j_middleware.BucketManager.BucketObject import BucketObject
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class Bucket:
    """

    """

    def __init__(self, global_id: str):
        self.GlobalId: str = global_id
        self.Content: List[BucketObject] = []

    def __repr__(self):
        return "Bucket - Model GUID {}".format(self.GlobalId)

    def __eq__(self, other):
        if self.GlobalId == other.GlobalId:
            return True
        else:
            return False

    def get_most_recent_object(self):
        pass


