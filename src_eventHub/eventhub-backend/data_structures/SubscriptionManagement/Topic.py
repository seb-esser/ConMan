import uuid
from typing import List

from data_structures.SubscriptionManagement.Subscription import Subscription


class Topic:
    """
    represents a subscription topic under which an event can be emitted.
    """

    def __init__(self, name: str, uuid_str: str = None):
        """

        :param name: topic name
        :param uuid_str: unique identifier for the topic. Created automatically if not specified
        """
        if uuid_str is None:
            self.uuid = uuid.uuid4().hex
        else:
            self.uuid = uuid_str
        self.name = name

        self.subscriptions: List[Subscription] = []

        self.sub_topics: List[Topic] = []

    def __repr__(self):
        return "Topic: {}".format(self.name)

    def get_subscriptions(self, recursive: bool = False):
        """
        returns all subscriptions registered in this topic
        :recursive:
        :return:
        """

        all_subscriptions = []

        # get also all subscriptions that are nested under the current topic
        if recursive:
            for sub_topic in self.sub_topics:
                sub = sub_topic.get_subscriptions(recursive=recursive)
                all_subscriptions.append(sub)

        else:
            all_subscriptions = self.subscriptions

        return all_subscriptions

    def add_subscription(self, subscriber):
        self.subscriptions.append(subscriber)

    def remove_subscription(self, subscriber):
        self.subscriptions.remove(subscriber)
