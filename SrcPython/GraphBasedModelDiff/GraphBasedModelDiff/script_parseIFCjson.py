
""" package import """
import json
import logging

""" class import """ 
from neo4j_middleware.IFCjson_neo4jMapper import IfcJsonNeo4jMapper
from neo4j_middleware.neo4jConnector import Neo4jConnector



# --- methods ---


# --- script ---
print('Parsing IfcJSON models to Neo4j....')

# init logging
logging.basicConfig(filename='myapp.log', level=logging.INFO)
logging.info('Started')


# open the json file
f_initial = open('./00_sampleData/IFC_json/spatial_initial.json', 'r') 
f_updated = open('./00_sampleData/IFC_json/spatial_updated.json', 'r') 
   # read the data
ifc_json_initial = json.load(f_initial)
ifc_json_updated = json.load(f_updated)
f_initial.close()
f_updated.close()

print('parsing json from post request body...') 
    
if ifc_json_initial == None:
    print('empty request body. please check. ')
else:
    print('IFC data ok.')

print('connecting to neo4j database... ')
connector = Neo4jConnector()
connector.connect_driver()

time_stamp_initial = 'version' + ifc_json_initial['timeStamp']
time_stamp_initial = time_stamp_initial.replace('-','')
time_stamp_initial = time_stamp_initial.replace(':','')

time_stamp_updated = 'version' + ifc_json_updated['timeStamp']
time_stamp_updated = time_stamp_updated.replace('-','')
time_stamp_updated = time_stamp_updated.replace(':','')

# --- Parse initial model ---
mapper_initial = IfcJsonNeo4jMapper(connector, time_stamp_initial)
# STEP 1: map all entities with their globalIds into the graph database
entities_initial = ifc_json_initial['data']
mapper_initial.mapEntities(entities_initial)

# STEP 2: set all attributes
for entity in entities_initial:
    attributes = entity.items()   
    mapper_initial.mapProperties(entity['globalId'], attributes)
                
# STEP 3: build objectified relationships
mapper_initial.mapObjectifiedRelationships()


# --- Parse updated model ---
mapper_updated = IfcJsonNeo4jMapper(connector, time_stamp_updated)
# STEP 1: map all entities with their globalIds into the graph database
entities_updated = ifc_json_updated['data']
mapper_updated.mapEntities(entities_updated)

# STEP 2: set all attributes
for entity in entities_updated:
    attributes = entity.items()   
    mapper_updated.mapProperties(entity['globalId'], attributes)
                
# STEP 3: build objectified relationships
mapper_updated.mapObjectifiedRelationships()




# finally disconnect
connector.disconnect_driver()       