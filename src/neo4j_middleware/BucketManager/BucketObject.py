class BucketObject:
    """

    """

    def __init__(self, ts, creation_date,  last_committed_version=False):
        self.timestamp = ts
        self.creation_date = creation_date
        self.last_committed_version: bool = last_committed_version

    def __repr__(self):
        return "BucketObject - Version timestamp {}".format(self.timestamp)


