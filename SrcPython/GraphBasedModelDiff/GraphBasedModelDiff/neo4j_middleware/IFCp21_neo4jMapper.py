
""" package import """
import ifcopenshell

""" file import """
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jGraphFactory import neo4jGraphFactory

class IFCp21_neo4jMapper:
    """description of class"""

    # constructor
    def __init__(self, myConnector, timestamp): 
        self.connector = myConnector
        self.timeStamp = timestamp
        super().__init__()

    # public entry
    def mapEntities(self, rootedEntities): 
        for entity in rootedEntities: 
            getDirectChildren(entity)

    # private recursive function
    def getDirectChildren(entity, indend): 
        print("".ljust(indend*4) + '{}'.format(entity))

        # print atomic attributes: 
        info = entity.get_info()
        entityId = info['id']
        entityType = info['type']
        # remove type and id from attrDict
        excludeKeys = ['id', 'type']
        attrs_dict = {key: val for key, val in info.items() if key not in excludeKeys }    
        
        # remove complex traversal attributes
        filtered_attrs = {}

        # remove traverse attrs
        for key, val in attrs_dict.items():
            if isinstance(val, str) or isinstance(val, float) or isinstance(val, int) or isinstance(val, bool) or isinstance(val, list) or isinstance(val, tuple): 
                filtered_attrs[key] = val
        if len(filtered_attrs.items()) > 0: 
            print("\t".ljust(indend*4) + '{}'.format(filtered_attrs))

        if 'wrappedValue' in info.keys(): 
            print(filtered_attrs['wrappedValue'])

        # neo4j: build node
        neo4jGraphFactory.CreateRootedNode(entityId, entityType, 'timestamp')
        # neo4j: append atomic properties



        # query all traversal entities
        children = model.traverse(entity, 1)

        children = children[1:]

        if len(children) == 0:
        #    print("".ljust(indend*4) + '{}'.format(entity))
        #    entity = children[0]
        #    entity_dict = entity.__dict__
        #    my_id = entity_dict['id']
        #    my_type = entity_dict['type']

        #    ## decode wrapped values

         

           
        #    ## toDo: append the value to the parent node

        #    exclude = ['id', 'type']
        #    attr_dict = {key: val for key, val in entity_dict.items() if key not in exclude}
        #    print("\t".ljust(indend*4) + '{}'.format(attr_dict))      

        #    return children
            pass
        else: 
        

            entity_dict = children[0].__dict__
            my_id = entity_dict['id']
            my_type = entity_dict['type']


            for child in children:
                children = getDirectChildren(child, indend + 1)

        return children




    #def map_entity_to_node(database, entity):
    #    # fetch all var names and assign attributes
    #    info = entity.get_info()
    #    class_name = info['type']
    #    instance_id = info['id']
    #    print("\tClass:\t" + class_name)
    #    print("\tEntityId:\t" + str(instance_id))

    #    # formulate cypher statement
    #    props_obj = {}
    #    cypher_statement = 'Create(n:' + class_name
    #    props_obj['EntityId'] = instance_id

    #    # parse attributes
    #    # stolen from: https://github.com/jakob-beetz/IfcOpenShellScriptingTutorial/wiki/02:-Inspecting-IFC-instance-objects
    #    for att_idx in range(0, len(entity) - 1):
    #        field_width = 20
    #        # In case we are dealing with a different IFC version
    #        # there might by attributes that do not exist in a 2x3 file
    #        # handle the attempt to print out a value where there is no
    #        # attribute gracefully
    #        try:
    #            att_name = entity.attribute_name(att_idx)
    #            att_type = entity.attribute_type(att_name)
    #            att_value = entity[att_idx]
    #            print("\t \t {}\t{}\t{}".format(att_name.ljust(field_width), att_type.ljust(field_width), att_value))

    #            # build properties json for cypher command
    #            if att_type == "AGGREGATE OF ENTITY INSTANCE":
    #                props_obj[att_name] = bin(att_value)
    #            else:
    #                props_obj[att_name] = att_value

    #            # ToDo: do something with complex attr_types
    #            # Ideas:
    #                # - recursively run though all sub-entities, create a sub-tree and hash this tree
    #        except:
    #            pass
    #        # print("\t \t" + str(var_name) + " \t " + str(att_type))

    #    # print(props_obj)

    #    formatted = format_json(props_obj)

    #    cypher_statement = cypher_statement + formatted + ')'
    #    print(cypher_statement)

    #    # perform insert operation on database
    #    database.run_cypher_statement(cypher_statement)
    #    print("")

    #def map_relationship_to_node(rel, database):
    #    # fetch all var names and assign attributes
    #    info = rel.get_info()
    #    class_name = info['type']
    #    instance_id = info['id']
    #    print("\tClass:\t" + class_name)
    #    print("\tEntityId:\t" + str(instance_id))

    #    # test if relationship connects two routed entities
    #    if hasattr(rel, 'RelatingObject') and hasattr(rel, 'RelatedObjects'):
    #        relatedElement = rel[4]
    #        relatingElements = rel[5]
    #        print('-> Related Object:')
    #        print(relatedElement)
    #        print('-> Relating Objects:')
    #        print(relatingElements)

    #        for i in range(0, len(relatingElements)-1):
    #            elemId = relatingElements[i].get_info()['id']

    #            cypher = ""
    #            cypher = cypher + 'MATCH(n) WHERE n.EntityId = "{}" \n'.format(relatedElement.get_info()['id'])
    #            cypher = cypher + 'MATCH(m) WHERE m.EntityId = "{}" \n'.format(elemId)
    #            cypher = cypher + 'merge (n) -[rel:IfcRelationship]->(m)'.format(class_name)

    #            database.run_cypher_statement(cypher)

    #def format_json(obj_dict):
    #    res_str = "{"
    #    for key, value in obj_dict.items():
    #        # try:
    #        #     res_str = res_str + key + ":" + value + ", "
    #        # except:
    #        res_str = res_str + key + ": '" + str(value) + "', "

    #    # remove last comma
    #    res_str = res_str[:-2]
    #    res_str = res_str + "}"
    #    return res_str
