import json
import os
import ifcopenshell

import sys
sys.path.append('../CM-client_pythonCOMMON')

from neo4jConnector import Neo4jConnector 
from IfcNeo4jMapper import IfcNeo4jMapper
# --- methods ---


# --- script ---
# check the entry point of your script
print(os.getcwd())

# open the json file
f = open('./processedModels/output_model01_v4.json', 'r') 
   # read the data
ifc_json = json.load(f)
f.close()


print('parsing json from post request body...') 
    
if ifc_json == None:
    print('empty request body. please check. ')

print('connecting to neo4j database... ')
connector = Neo4jConnector()
connector.connect_driver()
    
mapper = IfcNeo4jMapper()
try:
    # map all entities with their globalIds into the graph database
        entities = ifc_json['data']
        mapper.mapEntities(entities)

        # STEP 2: set all attributes
        for entity in entities:
            attributes = entity.items()
            mapper.mapAttributes(attributes)

             
except :
    pass
   
connector.disconnect_driver()       