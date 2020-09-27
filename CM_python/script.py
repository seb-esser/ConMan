import json
import os
import ifcopenshell

from pycommon.ifcNeo4jMapper import IfcNeo4jMapper
from pycommon.neo4jConnector import Neo4jConnector



# --- methods ---


# --- script ---
# check the entry point of your script
print(os.getcwd())

# open the json file
f = open('./processedModels/spatial.json', 'r') 
   # read the data
ifc_json = json.load(f)
f.close()


print('parsing json from post request body...') 
    
if ifc_json == None:
    print('empty request body. please check. ')
else:
    print('IFC data ok.')

print('connecting to neo4j database... ')
connector = Neo4jConnector()
connector.connect_driver()
 
mapper = IfcNeo4jMapper(connector)


# map all entities with their globalIds into the graph database
entities = ifc_json['data']
mapper.mapEntities(entities)

# STEP 2: set all attributes
for entity in entities:
    attributes = entity.items()   
    mapper.mapProperties(entity['globalId'], attributes)
                
# STEP 3: build objectified relationships
mapper.mapObjectifiedRelationships()

# finally disconnect
connector.disconnect_driver()       