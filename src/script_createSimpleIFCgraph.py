from IfcGraphInterface.Ifc2GraphTranslator import IFCGraphGenerator
from neo4j_middleware.neo4jConnector import Neo4jConnector

path = './00_sampleData/IFC_stepP21/wand_tuer/01_Wand_single-guidsMod.ifc'

connector = Neo4jConnector()
connector.connect_driver()

# parse model
graph_generator = IFCGraphGenerator(connector, path, None, write_to_file=True)

graph_generator.generateGraph()
