# This is a test script to showcase:
# 1. load two IFC models
# 2. diff models
# 3. formulate patch

# 4. load init model once again but with modified time stamp

# 5. apply patch

# 6. create IFC model out of the updated graph
from IfcGraphInterface.Ifc2GraphTranslator import IFCGraphGenerator
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

# 0 clear database
connector.run_cypher_statement('MATCH (n) DETACH DELETE n')

# 1 load models into graph
model_name_init = './00_sampleData/IFC_stepP21/GeomRepresentation_05/cube_single.ifc'
model_name_updated = './00_sampleData/IFC_stepP21/GeomRepresentation_05/cube_double.ifc'

print('STEP 1: Generate graph initial and graph updated... ')
graphGenerator_init = IFCGraphGenerator(connector, model_name_init, None)
graphGenerator_init.generateGraph()

graphGenerator_updated = IFCGraphGenerator(connector, model_name_updated, None)
graphGenerator_updated.generateGraph()
print('Graphs generated successfully')

# 2 diff models




