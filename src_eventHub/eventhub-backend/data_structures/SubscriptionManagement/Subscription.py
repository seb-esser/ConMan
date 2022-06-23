from data_structures.Teams.Subscriber import Subscriber


class Subscription:

    def __init__(self, subscribing_party: Subscriber, level: str = "INFO", notification_interval: int = 3600, ):
        """
        represents a subscription and knows about the notification level and interval
        :param level: specifies the desired escalation level (warning, info, silent)
        :param notification_interval: default is 3600 sec, can be 0 for real-time notification
        :param subscribing_party: the subscriber who has placed the subscription
        """

        self.level = level
        self.notification_interval = notification_interval
        self.subscriber: Subscriber = subscribing_party

