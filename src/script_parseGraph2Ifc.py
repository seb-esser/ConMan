
from IfcGraphInterface.Graph2IfcTranslator import Graph2IfcTranslator
from neo4j_middleware.neo4jConnector import Neo4jConnector

def main():
    connector = Neo4jConnector()
    connector.connect_driver()

    ts = "ts20221001T111540"

    # init generator instance
    generator = Graph2IfcTranslator(connector=connector, ts=ts)

    # load data into IFC
    generator.generate_SPF()

    # save model as IFC SPF file
    path = "C:\dev\out\{}.ifc".format(ts)
    generator.save_model(path=path)

    # disconnect driver
    connector.disconnect_driver()


if __name__ == "__main__":
    main()
