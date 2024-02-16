from IfcGraphInterface.Ifc2GraphTranslator import IFCGraphGenerator
from neo4j_middleware.neo4jConnector import Neo4jConnector


def main():
    connector = Neo4jConnector()
    path = r"C:\Users\sesse\OneDrive - TUM\01_TUMCMS\00_Promotion\dev\GeometrySeparation\GeometrySeparation.ifc"

    generator = IFCGraphGenerator(connector, path, None)
    generator.generate_arrows_visualization(ignore_null_values=True)


if __name__ == "__main__":
    main()
