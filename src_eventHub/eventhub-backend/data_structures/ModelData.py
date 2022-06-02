class ModelData:
    def __init__(self, name):
        self.Name = name
        self.timestamps = []

    def set_timestamps(self, ts):
        self.timestamps.append(ts)

