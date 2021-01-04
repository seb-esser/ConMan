
""" package import """
import ifcopenshell
import logging
import datetime

""" class import """
from neo4j_middleware.IFCp21_neo4jMapper import IFCp21_neo4jMapper
from neo4j_middleware.neo4jGraphFactory import neo4jGraphFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector


# --- defs ---
def parseModel(connector, model_path):
	# open model
	model = ifcopenshell.open(model_path)
	# extract time stamp and use it as the identifier inside the resulting graph
	label = 'ts' + model.wrapped_data.header.file_name.time_stamp
	label = label.replace('-','')
	label = label.replace(':','')
		
	## DEBUG ONLY! delete entire graph: 
	print('DEBUG INFO: entire graph gets deleted')
	connector.run_cypher_statement('MATCH(n:{}) DETACH DELETE n'.format(label))

	print('Parsing IFC model. Label: {}'.format(label))

	# extract model data
	obj_definitions =  model.by_type('IfcObjectDefinition')
	obj_relationships = model.by_type('IfcRelationship')
	props = model.by_type('IfcProperty')
	
	# init mapper
	mapper = IFCp21_neo4jMapper(connector, label, model)

	# parse rooted node + subgraphs
	mapper.mapEntities(obj_definitions)
	
	# parse objectified relationships
	mapper.mapObjRelationships(obj_relationships)

	# parse properties
	# ToDo 
	
	# post processing: remove all p21 ids
	cypher = 'MATCH(n:{}) REMOVE n.p21_id '.format(label)



# --- Script --- 

# init logging
logging.basicConfig(filename='myapp.log', level=logging.INFO)
logging.info('Started')

print('Parsing Ifc StepP21 model to Neo4j.... \n')
print('connecting to neo4j database... ')
connector = Neo4jConnector(False, True)
connector.connect_driver()


model_path = './00_sampleData/IFC_stepP21/sampleModel4x1.ifc'

# parse model
parseModel(connector, model_path)


# disconnect from database
connector.disconnect_driver()

