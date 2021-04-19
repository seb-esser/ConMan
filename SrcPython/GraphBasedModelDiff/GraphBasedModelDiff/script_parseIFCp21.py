
""" package import """
import ifcopenshell
import logging
import datetime
import os
import progressbar

""" class import """
from neo4j_middleware.IFCp21_neo4jMapper import IFCp21_neo4jMapper
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
# These lines all filepaths in the directory 'dir'
dir = './00_sampleData/IFC_stepP21/GeomRepresentation_01' 
paths = []
for path in os.listdir(dir):
    full_path = os.path.join(dir, path)
    if os.path.isfile(full_path):
        paths.append(full_path)

#paths = ['./00_sampleData/IFC_stepP21/GeomRepresentation_01/Initial_GeomRepresentation_01.ifc' # same representation
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
#		 './00_sampleData/IFC_stepP21/Residential_01/residential_updated.ifc'
#		 ]

increment = 100/len(paths)
percent = 0
print('Starting to generate graphs...')
for path in paths: 
    progressbar.printbar(percent)
    # parse model
    graphGenerator = IFCp21_neo4jMapper(connector, path, None)

    graphGenerator.generateGraph()

    percent += increment
print('\n 100% done. Graphs generated.')	
# disconnect from database
connector.disconnect_driver()

