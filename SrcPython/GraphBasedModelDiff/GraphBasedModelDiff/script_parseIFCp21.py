
""" package import """
import ifcopenshell

""" class import """
from .neo4j_middleware.IFCp21_neo4jMapper import IFCp21_neo4jMapper
from .neo4j_middleware.neo4jConnector import Neo4jConnector

# --- Script --- 

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
    IFCp21_neo4jMapper.map_entity_to_node(database, objDef)

# print('PropertyDefinitions: ')
# for propDef in propDefs:
    # print("\t" + str(propDef))

print('Relationships: ')
for rel in rels:
    # print("\t" + str(rel))
    IFCp21_neo4jMapper.map_relationship_to_node(rel, database)

