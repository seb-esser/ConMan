from data_structures.SubscriptionManagement.Subscription import Subscription
from data_structures.Teams.Subscriber import Subscriber


class NotificationSubscription(Subscription):

    def __init__(self, subscribing_party: Subscriber, level: str = "INFO", notification_interval: int = 3600):
        super().__init__(subscribing_party, level, notification_interval)


