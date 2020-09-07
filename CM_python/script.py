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
f = open('./processedModels/output_model01_v4.json', 'r') 
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

    # removing id and type from attributes -> already parsed
    exlude = ['globalId', 'type']
    resultset = {key: val for key,val in attributes if key not in exlude}
    
    # reduced attributes
    reduced_attributes = resultset.items()
    mapper.mapAttributes(reduced_attributes, entity['globalId'], True)
                

# finally disconnect
connector.disconnect_driver()       