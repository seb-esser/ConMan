class BucketObject:
    """
    A BucketObject models a version-controlled item in the database. It can be a BIM-model or any other piece of data
    following object-oriented principles.
    """

    def __init__(self, ts, creation_date,  last_committed_version=False):
        self.timestamp = ts
        self.creation_date = creation_date
        self.last_committed_version: bool = last_committed_version

    def __repr__(self):
        return "BucketObject - Version timestamp {}".format(self.timestamp)

    def __lt__(self, other):
        return self.creation_date < other.creation_date

    def __gt__(self, other):
        return self.creation_date > other.creation_date
