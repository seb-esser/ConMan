from IfcGraphInterface.Ifc2GraphTranslator import IFCGraphGenerator
from neo4j_middleware.neo4jConnector import Neo4jConnector


def main():
    connector = Neo4jConnector()
    path = '00_sampleData/IFC_stepP21/diss_samples/bsp3-CompModified.ifc'

    generator = IFCGraphGenerator(connector, path, None)
    generator.generate_arrows_visualization(ignore_null_values=True)


if __name__ == "__main__":
    main()
