
""" package import """
import ifcopenshell

""" class import """
from neo4j_middleware.IFCp21_neo4jMapper import IFCp21_neo4jMapper
from neo4j_middleware.neo4jConnector import Neo4jConnector


# --- defs ---

def getDirectChildren(entity, indend): 
    
    children = model.traverse(entity, 1)

    if len(children) == 1:
        print("".ljust(indend*4) + '{}'.format(entity))
        entity = children[0]
        entity_dict = entity.__dict__
        my_id = entity_dict['id']
        my_type = entity_dict['type']

        # decode wrapped values

      
        if 'wrappedValue' in entity_dict.keys(): 
            print('measure')
            # toDo: append the value to the parent node


        exclude = ['id', 'type']
        attr_dict = {key: val for key, val in entity_dict.items() if key not in exclude}
        print("\t".ljust(indend*4) + '{}'.format(attr_dict))

        

        return children
    else: 
        print("".ljust(indend*4) + '{}'.format(entity))

        entity_dict = children[0].__dict__
        my_id = entity_dict['id']
        my_type = entity_dict['type']


        for child in children[1:]:
            children = getDirectChildren(child, indend + 1)


# --- Script --- 

print('TestScript to map a given IFC model into a simplified Neo4j graph \n')

model_path = './00_sampleData/IFC_stepP21/sampleModel4x2.ifc'

model = ifcopenshell.open(model_path)

# --- get all rooted entities -> GUID exists ---

# loop over all entities
for obj_definition in model.by_type('IfcObjectDefinition'): 
    print(obj_definition)

    getDirectChildren(obj_definition, 0)
    

        
















## get entiy
#site = model.by_type('IfcSite')[0]
#pt_entity = model.by_id(43)

## all sub references
#all_traverses = model.traverse(pt_entity)
## all inverse pointers
#all_inverses = model.get_inverse(pt_entity)

#print('traverses')
#for traverse in all_traverses: 
#    print('\t {}'.format(traverse))

#print('Inverses')
#for inverse in all_inverses:
#    print('\t {}'.format(inverse))

## get all entity types used in the staged IFC model
#print(model.types())
#print(pt_entity.type())

#objDefs = model.by_type('IfcObjectDefinition')
#propDefs = model.by_type('IfcPropertyDefinition')
#rels = model.by_type('IfcRelationship')

## -- setup database connection
#database = Neo4jConnector()
#database.connect_driver()

## control output to console
#print('ObjectDefinitions: ')
#for objDef in objDefs:
#    print("\t" + str(objDef))
#    # IFCp21_neo4jMapper.map_entity_to_node(database, objDef)

## print('PropertyDefinitions: ')
## for propDef in propDefs:
#    # print("\t" + str(propDef))

#print('Relationships: ')
#for rel in rels:
#    print("\t" + str(rel))
#    # IFCp21_neo4jMapper.map_relationship_to_node(rel, database)

