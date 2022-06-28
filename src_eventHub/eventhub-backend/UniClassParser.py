import csv
from data_structures.SubscriptionManagement.SubscriptionModel import SubscriptionModel
from data_structures.SubscriptionManagement.Topic import Topic
import jsonpickle

model = SubscriptionModel(name="Uniclass Breakdown")

with open('data_structures/SubscriptionManagement/models/Uniclass2015_Pr.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    #Einträge der Reihe nach einlesen
    for row in reader:
        #print(row)
        #print(row['Code'], row['Title'])
        test_str = row['Code']
        counter = test_str.count('_')
        #in Abhängigkeit der hierarchy structure zuordnen und einlesen
        if counter == 1:
            group = Topic(row['Title'], row['Code'])
            model.topics.extend([group])
            print(group)
        elif counter == 2:
            sub_group = Topic(row['Title'], row['Code'])
            group.sub_topics.extend([sub_group])
        elif counter == 3:
            section = Topic(row['Title'], row['Code'])
            sub_group.sub_topics.extend([section])
        elif counter == 4:
            object = Topic(row['Title'], row['Code'])
            section.sub_topics.extend([object])
        else:
            break

    model.to_json("")


