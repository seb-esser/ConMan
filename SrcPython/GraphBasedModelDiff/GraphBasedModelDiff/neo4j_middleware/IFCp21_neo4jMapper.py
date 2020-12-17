
""" package import """
import ifcopenshell

""" file import """
from neo4j_middleware.neo4jConnector import Neo4jConnector

class IFCp21_neo4jMapper:
    """description of class"""


    def map_entity_to_node(database, entity):
        # fetch all var names and assign attributes
        info = entity.get_info()
        class_name = info['type']
        instance_id = info['id']
        print("\tClass:\t" + class_name)
        print("\tEntityId:\t" + str(instance_id))

        # formulate cypher statement
        props_obj = {}
        cypher_statement = 'Create(n:' + class_name
        props_obj['EntityId'] = instance_id

        # parse attributes
        # stolen from: https://github.com/jakob-beetz/IfcOpenShellScriptingTutorial/wiki/02:-Inspecting-IFC-instance-objects
        for att_idx in range(0, len(entity) - 1):
            field_width = 20
            # In case we are dealing with a different IFC version
            # there might by attributes that do not exist in a 2x3 file
            # handle the attempt to print out a value where there is no
            # attribute gracefully
            try:
                att_name = entity.attribute_name(att_idx)
                att_type = entity.attribute_type(att_name)
                att_value = entity[att_idx]
                print("\t \t {}\t{}\t{}".format(att_name.ljust(field_width), att_type.ljust(field_width), att_value))

                # build properties json for cypher command
                if att_type == "AGGREGATE OF ENTITY INSTANCE":
                    props_obj[att_name] = bin(att_value)
                else:
                    props_obj[att_name] = att_value

                # ToDo: do something with complex attr_types
                # Ideas:
                    # - recursively run though all sub-entities, create a sub-tree and hash this tree
            except:
                pass
            # print("\t \t" + str(var_name) + " \t " + str(att_type))

        # print(props_obj)

        formatted = format_json(props_obj)

        cypher_statement = cypher_statement + formatted + ')'
        print(cypher_statement)

        # perform insert operation on database
        database.run_cypher_statement(cypher_statement)
        print("")

    def map_relationship_to_node(rel, database):
        # fetch all var names and assign attributes
        info = rel.get_info()
        class_name = info['type']
        instance_id = info['id']
        print("\tClass:\t" + class_name)
        print("\tEntityId:\t" + str(instance_id))

        # test if relationship connects two routed entities
        if hasattr(rel, 'RelatingObject') and hasattr(rel, 'RelatedObjects'):
            relatedElement = rel[4]
            relatingElements = rel[5]
            print('-> Related Object:')
            print(relatedElement)
            print('-> Relating Objects:')
            print(relatingElements)

            for i in range(0, len(relatingElements)-1):
                elemId = relatingElements[i].get_info()['id']

                cypher = ""
                cypher = cypher + 'MATCH(n) WHERE n.EntityId = "{}" \n'.format(relatedElement.get_info()['id'])
                cypher = cypher + 'MATCH(m) WHERE m.EntityId = "{}" \n'.format(elemId)
                cypher = cypher + 'merge (n) -[rel:IfcRelationship]->(m)'.format(class_name)

                database.run_cypher_statement(cypher)

    def format_json(obj_dict):
        res_str = "{"
        for key, value in obj_dict.items():
            # try:
            #     res_str = res_str + key + ":" + value + ", "
            # except:
            res_str = res_str + key + ": '" + str(value) + "', "

        # remove last comma
        res_str = res_str[:-2]
        res_str = res_str + "}"
        return res_str

