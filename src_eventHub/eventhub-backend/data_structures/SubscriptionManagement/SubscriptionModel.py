import uuid
from typing import List

import jsonpickle

from data_structures.SubscriptionManagement.Topic import Topic
from data_structures.Teams.Subscriber import Subscriber


class SubscriptionModel:
    """entry class for entire subscription hierarchies including load and dump functions"""

    def __init__(self, name: str, uuid_str: str = None):
        self.name: str = name
        self.topics: List[Topic] = []

        if uuid_str is None:
            self.uuid = uuid.uuid4().hex
        else:
            self.uuid = uuid_str

    def __repr__(self):
        return "SubscriptionModel {}".format(self.name)

    def add_topic(self, topic):
        self.topics.append(topic)

    @classmethod
    def from_json(cls, name: str = None, path: str = None):
        """
        create object from json
        :return:
        """

        json_file = None

        # save file to disk
        if name is not None:
            json_file = open("SubscriptionModel_{}.json".format(name), "r")
        elif path is not None:
            json_file = open(path, "r")
        content = json_file.read()
        json_file.close()
        js = jsonpickle.loads(content)
        return js

    def to_json(self, file_path: str = None):
        """
        serialize object into JSON representation
        :param file_path:
        :return:
        """

        res = jsonpickle.dumps(self)

        if file_path is not None:
            #     save file to disk
            json_file = open("SubscriptionModel_{}.json".format(self.name).replace(' ', ''), "w")
            json_file.write(res)
            json_file.close()

        return res

    def evaluate_dependency_subs(self, patch):
        raise NotImplementedError("this method is not yet implemented. ")
        pass

