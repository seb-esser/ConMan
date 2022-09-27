from datetime import datetime
from pprint import pprint

from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


def get_status():
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

    print("Tracked model versions:")

    return_dict = {}
    for z in zipped:
        project_guid = z[0].attrs["GlobalId"]
        project_name = z[0].attrs["Name"]
        created = int(z[1].attrs["CreationDate"])
        creation_date = datetime.utcfromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S')
        timestamp = z[0].get_timestamps()[0]
        print("\t{0}\t{1}\t{2}\t{3}".format(timestamp, creation_date, project_guid, project_name))
        return_dict[timestamp] = project_guid

    connector.disconnect_driver()

    return return_dict


if __name__ == "__main__":
    get_status()
