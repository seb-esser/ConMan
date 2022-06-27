import jsonpickle

from data_structures.SubscriptionManagement.SubscriptionModel import SubscriptionModel
from data_structures.SubscriptionManagement.Topic import Topic


def main():

    model = SubscriptionModel(name="IFC Breakdown")
    arch = Topic(name="Domain Model Architectural Domain")
    mep = Topic(name="Domain Model MEP Domain")
    hvac = Topic(name="Domain Model HVAC")

    model.topics.extend([arch, mep, hvac])

    topic_bld_a = Topic("Building A")
    topic_bld_b = Topic("Building B")

    storey_a_1 = Topic("Storey 1")
    storey_a_1.sub_topics.extend(
        [Topic("Wall"),
         Topic("Window"),
         Topic("Door"),
         Topic("Slab"),
         Topic("Column")])

    storey_a_2 = Topic("Storey 2")
    storey_a_2.sub_topics.extend(
        [Topic("Wall"),
         Topic("Window"),
         Topic("Door"),
         Topic("Slab"),
         Topic("Column")])

    storey_a_3 = Topic("Storey 3")
    storey_a_3.sub_topics.extend(
        [Topic("Wall"),
         Topic("Window"),
         Topic("Roof")
         ])

    storey_b_1 = Topic("Storey 1")
    storey_b_2 = Topic("Storey 2")

    topic_bld_a.sub_topics.extend([storey_a_1, storey_a_2, storey_a_3])
    topic_bld_b.sub_topics.extend([storey_b_1, storey_b_2])

    arch.sub_topics.extend([topic_bld_a, topic_bld_b])

    model.to_json("")


if __name__ == "__main__":
    main()
