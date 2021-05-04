""" package import """
import logging

""" class import """
from IfcGraphInterface.Ifc2GraphTranslator import IFCGraphGenerator
from neo4j_middleware.neo4jConnector import Neo4jConnector

# --- Script ---

# init logging
logging.basicConfig(filename='myapp.log', level=logging.INFO)
logging.info('Started')

print('Parsing Ifc StepP21 model to Neo4j.... \n')
print('connecting to neo4j database... ')
connector = Neo4jConnector(False, True)
connector.connect_driver()

# # These lines all filepaths in the directory 'dir'
#dir = './00_sampleData/IFC_stepP21/**/*.ifc'
#paths = []
#for filepath in glob.glob(dir, recursive=True):
#    paths.append(filepath)
#print(paths)

paths = ['./00_sampleData/IFC_stepP21/GeomRepresentation_01/Initial_GeomRepresentation_01.ifc',  # same representation
         './00_sampleData/IFC_stepP21/GeomRepresentation_01/Update_GeomRepresentation_01.ifc',  # two representations
         './00_sampleData/IFC_stepP21/GeomRepresentation_02/Initial_GeomRepresentation_02.ifc',	# two representations
         './00_sampleData/IFC_stepP21/GeomRepresentation_02/Update_GeomRepresentation_02.ifc',	# elevated cuboid height -> PMod
         './00_sampleData/IFC_stepP21/GeomRepresentation_03/Initial_GeomRepresentation_03.ifc',	# 1 proxy as cuboid
         './00_sampleData/IFC_stepP21/GeomRepresentation_03/Update_GeomRepresentation_03.ifc',	# 1 proxy as cylinder -> mainly PMod,
         './00_sampleData/IFC_stepP21/GeomRepresentation_04/Initial_GeomRepresentation_04.ifc',	# extrudedArea
         './00_sampleData/IFC_stepP21/GeomRepresentation_04/Update_GeomRepresentation_04.ifc',	# BRep -> structural Mod
         './00_sampleData/IFC_stepP21/wall-column/Wall-Column.ifc',
         './00_sampleData/IFC_stepP21/wall-column/Column-Wall.ifc',
         './00_sampleData/IFC_stepP21/SleeperSample/sleeper_init.ifc',
         './00_sampleData/IFC_stepP21/SleeperSample/sleeper_updated.ifc',
         './00_sampleData/IFC_stepP21/SpatialStructure_01/spatial_initial.ifc',
         './00_sampleData/IFC_stepP21/SpatialStructure_01/spatial_updated.ifc',
         './00_sampleData/IFC_stepP21/LocalPlacement_01/Initial_LocalPlacement_01.ifc',
         './00_sampleData/IFC_stepP21/LocalPlacement_01/Update_LocalPlacement_01.ifc'
         ]
for p in paths: 
    print(p)


print('Starting to generate graphs...')
for path in paths:
    # parse model
    graphGenerator = IFCGraphGenerator(connector, path, None)

    graphGenerator.generateGraph()
print('\n 100% done. Graphs generated.')
# disconnect from database
connector.disconnect_driver()
