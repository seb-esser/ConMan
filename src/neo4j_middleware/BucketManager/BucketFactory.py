from datetime import datetime
from typing import List

from neo4j_middleware.BucketManager.Bucket import Bucket
from neo4j_middleware.BucketManager.BucketObject import BucketObject
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class BucketUtility:

    def __init__(self):
        pass

    def get_buckets(self):
        connector = Neo4jConnector()
        connector.connect_driver()

        cy = "MATCH (n:PrimaryNode {EntityType: \"IfcProject\"})-->(h:SecondaryNode{EntityType: \"IfcOwnerHistory\"}) " \
             "RETURN n"
        raw = connector.run_cypher_statement(cy)

        project_nodes = NodeItem.from_neo4j_response(raw)

        cy = "MATCH (n:PrimaryNode {EntityType: \"IfcProject\"})-->(h:SecondaryNode{EntityType: \"IfcOwnerHistory\"}) " \
             "RETURN h"
        raw = connector.run_cypher_statement(cy)

        history_nodes = NodeItem.from_neo4j_response(raw)

        zipped = zip(project_nodes, history_nodes)

        buckets = []

        for z in zipped:
            project_guid = z[0].attrs["GlobalId"]

            project_name = z[0].attrs["Name"]
            created = int(z[1].attrs["CreationDate"])
            creation_date = datetime.utcfromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S')
            timestamp = z[0].get_timestamps()[0]

            bucket_object = BucketObject(ts=timestamp, creation_date=creation_date)

            existing_bucket = [x for x in buckets if x.GlobalId == project_guid]
            if len(existing_bucket) == 0:
                bucket = Bucket(global_id=project_guid)
                bucket.Content.append(bucket_object)
                buckets.append(bucket)
            else:
                existing_bucket[0].Content.append(bucket_object)

        connector.disconnect_driver()
        return buckets

    def pprint_buckets(self, buckets: List[Bucket]):

        print("Tracked buckets:")
        for bucket in buckets:
            print("Bucket ID {}".format(bucket.GlobalId))

            for version in bucket.Content:
                print("\t timestamp: {} created: {}".format(version.timestamp, version.creation_date))
