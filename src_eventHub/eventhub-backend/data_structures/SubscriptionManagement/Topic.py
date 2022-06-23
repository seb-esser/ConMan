import uuid


class Topic:
    def __init__(self, name: str, uuid_str: str = None):
        if uuid_str is None:
            self.uuid = uuid.UUID.hex
        else:
            self.uuid = uuid_str
        self.Name = name

        self.subscribers = []

        self.sub_topics = []

    def get_subscribers(self):
        return [subscriber.uuid for subscriber in self.subscribers]

    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber):
        self.subscribers.remove(subscriber)
