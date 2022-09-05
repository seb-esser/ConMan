from typing import List

from data_structures.SubscriptionManagement.DependencyCriterion import DependencyCriterion
from data_structures.SubscriptionManagement.Subscription import Subscription
from data_structures.Teams.Subscriber import Subscriber


class DependencySubscription(Subscription):

    def __init__(self, subscribing_party: Subscriber, level: str = "INFO", notification_interval: int = 3600):
        super().__init__(subscribing_party=subscribing_party, level=level, notification_interval=notification_interval)
        self.criteria: List[DependencyCriterion] = []

    def add_criterion(self, criterion: DependencyCriterion):
        """

        :param criterion:
        :return:
        """
        self.criteria.append(criterion)

