import csv
from data_structures.SubscriptionManagement.SubscriptionModel import SubscriptionModel
from data_structures.SubscriptionManagement.Topic import Topic
import jsonpickle

def main():

    model = SubscriptionModel(name="Uniclass Breakdown")

    with open('data_structures/SubscriptionManagement/models/Uniclass2015_Pr.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            test_str = row['Code']
            counter = test_str.count('_')

            if counter == 1:
                group = Topic(row['Title'])
                model.topics.extend([group])
            elif counter == 2:
                sub_group = Topic(row['Title'])
                group.sub_topics.extend([sub_group])
            elif counter == 3:
                section = Topic(row['Title'])
                sub_group.sub_topics.extend([section])
            elif counter == 4:
                object_section = Topic(row['Title'])
                section.sub_topics.extend([object_section])
            else:
                break

        model.to_json()


if __name__ == "__main__":
    main()
