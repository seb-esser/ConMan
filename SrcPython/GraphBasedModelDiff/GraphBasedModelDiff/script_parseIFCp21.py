
""" package import """
import ifcopenshell
import logging
import datetime

""" class import """
from neo4j_middleware.IFCp21_MetaGraphGenerator import IFCp21_MetaGraphGenerator
from neo4j_middleware.neo4jGraphFactory import neo4jGraphFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector


# --- Script --- 

# init logging
logging.basicConfig(filename='myapp.log', level=logging.INFO)
logging.info('Started')

print('Parsing Ifc StepP21 model to Neo4j.... \n')
print('connecting to neo4j database... ')
connector = Neo4jConnector(False, True)
connector.connect_driver()

# ToDo: automate loading of unit tests. See ticket #16 in the Gitlab repo. 
paths = [
#		 './00_sampleData/IFC_stepP21/GeomRepresentation_01/Initial_GeomRepresentation_01.ifc', # same representation
#		 './00_sampleData/IFC_stepP21/GeomRepresentation_01/Update_GeomRepresentation_01.ifc',  # two representations
#		 './00_sampleData/IFC_stepP21/GeomRepresentation_02/Initial_GeomRepresentation_02.ifc',	# two representations
#		 './00_sampleData/IFC_stepP21/GeomRepresentation_02/Update_GeomRepresentation_02.ifc',	# elevated cuboid height -> PMod
#		 './00_sampleData/IFC_stepP21/GeomRepresentation_03/Initial_GeomRepresentation_03.ifc',	# 1 proxy as cuboid 
#		 './00_sampleData/IFC_stepP21/GeomRepresentation_03/Update_GeomRepresentation_03.ifc',	# 1 proxy as cylinder -> mainly PMod, 
#		 './00_sampleData/IFC_stepP21/GeomRepresentation_04/Initial_GeomRepresentation_04.ifc',	# extrudedArea
#		 './00_sampleData/IFC_stepP21/GeomRepresentation_04/Update_GeomRepresentation_04.ifc',	# BRep -> structural Mod
#		 './00_sampleData/IFC_stepP21/wall-column/Wall-Column.ifc', 
#		 './00_sampleData/IFC_stepP21/wall-column/Column-Wall.ifc', 
#		 './00_sampleData/IFC_stepP21/SleeperSample/sleeper_init.ifc', 
#		 './00_sampleData/IFC_stepP21/SleeperSample/sleeper_updated.ifc', 
#		 './00_sampleData/IFC_stepP21/Residential_01/residential_init.ifc', 
#		 './00_sampleData/IFC_stepP21/Residential_01/residential_updated.ifc',
		 './00_sampleData/IFC_stepP21/Beam_extrudedGeom/beam-extruded-solid_initial.ifc', 
		 './00_sampleData/IFC_stepP21/Beam_extrudedGeom/beam-extruded-solid_updated.ifc'
		 ]

for path in paths: 
	# parse model

	graphGenerator = IFCp21_MetaGraphGenerator(connector, path, None)
	graphGenerator.generateGraph()
	graphGenerator.validateParsingResult()
	
# disconnect from database
connector.disconnect_driver()

