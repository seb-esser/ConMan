import os

from IfcGraphInterface.Graph2IfcTranslator import Graph2IfcTranslator
from neo4j_middleware.neo4jConnector import Neo4jConnector


def parse(ts: str, directory=None):
    """
    translates a graph specified by its timestamp back into a file representation and stores it in the given directory
    """

    # connect to db
    connector = Neo4jConnector()
    connector.connect_driver()

    if directory is None:
        directory = "C:\dev\out"

    # ensure path is valid
    if not os.path.exists(directory):
        raise NotADirectoryError("The directory you have specified is not reachable. Stopping export. ")

    # init generator instance
    generator = Graph2IfcTranslator(connector=connector, ts=ts, schema_identifier='IFC4')

    # load data into IFC
    generator.generate_SPF()

    # save model
    full_directory_path = "{}\{}.ifc".format(directory, ts)
    generator.save_model(full_directory_path)

    print("Model saved: {}".format(full_directory_path))

    # disconnect driver
    connector.disconnect_driver()
