from typing import List


from neo4j_middleware.BucketManager.BucketObject import BucketObject


class Bucket:
    """
    A bucket contains information about the different versions of a model in the database.
    More precisely, it provides the available timestamps and has methods to determine the most recent and
    the last committed version
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

    def get_most_recent_version(self) -> BucketObject:
        """
        returns the most recent BucketObject of this bucket
        """
        return self.Content[-1]

    def get_last_committed_version(self) -> BucketObject:
        """
        returns the last committed object. If no object has been submitted, the first item is returned
        """
        last_committed_object = [x for x in self.Content if x.last_committed_version is True]

        if len(last_committed_object) < 0:
            return last_committed_object[0]
        else:
            return self.Content[0]

