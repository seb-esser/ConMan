import ifcopenshell
from neo4jConnector import Neo4jConnector


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
