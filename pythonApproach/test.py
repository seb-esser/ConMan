# libs
import ifcopenshell

# own functions
from MapRelationshipToNode import map_relationship_to_node
from MapEntityToNode import map_entity_to_node

# Script body
from neo4jConnector import Neo4jConnector

print('TestScript to map a given IFC model into a simplified Neo4j graph \n')
model = ifcopenshell.open('sampleModel4x2.ifc')

# --- get all rooted entities -> GUID exists ---
objDefs = model.by_type('IfcObjectDefinition')
propDefs = model.by_type('IfcPropertyDefinition')
rels = model.by_type('IfcRelationship')

# -- setup database connection
database = Neo4jConnector()
database.connect_driver()

# control output to console
print('ObjectDefinitions: ')
for objDef in objDefs:
    # print("\t" + str(objDef))
    map_entity_to_node(database, objDef)

# print('PropertyDefinitions: ')
# for propDef in propDefs:
    # print("\t" + str(propDef))

print('Relationships: ')
for rel in rels:
    # print("\t" + str(rel))
    map_relationship_to_node(rel, database)

