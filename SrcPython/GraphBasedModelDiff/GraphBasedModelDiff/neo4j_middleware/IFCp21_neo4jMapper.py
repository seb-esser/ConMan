
""" package import """
import ifcopenshell

""" file import """
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jGraphFactory import neo4jGraphFactory
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory
from common_base.ifcMapper import IfcMapper

class IFCp21_neo4jMapper(IfcMapper):
    """description of class"""

    # constructor
    def __init__(self, myConnector, timestamp, my_model): 
        self.connector = myConnector
        self.timeStamp = timestamp
        self.model = my_model
        super().__init__()

    # public entry
    def mapEntities(self, rootedEntities): 
        for entity in rootedEntities: 
        
            info = entity.get_info()
            entityId = info['GlobalId']
            entityType = info['type']

            # neo4j: build node
            cypher_statement = neo4jGraphFactory.CreateRootedNode(entityId, entityType, self.timeStamp)
            node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

            
            # get all attrs and children
            self.getDirectChildren(entity, 0, node_id[0])

    # private recursive function
    def getDirectChildren(self, entity, indend, parent_NodeId=None): 
        print("".ljust(indend*4) + '{}'.format(entity))

        # print atomic attributes: 
        info = entity.get_info()
        p21_id = info['id']
        entityType = info['type']
        # remove type and id from attrDict
        excludeKeys = ['id', 'type']        
        attrs_dict = {key: val for key, val in info.items() if key not in excludeKeys }    
        
        # remove complex traversal attributes
        filtered_attrs = {}
        filtered_attrs['p21_id'] = p21_id
        # remove traverse attrs
        for key, val in attrs_dict.items():
            if isinstance(val, str) or isinstance(val, float) or isinstance(val, int) or isinstance(val, bool) or isinstance(val, list) : 
                filtered_attrs[key] = val
            # ToDo: handle special situation with tuples
            elif isinstance(val, tuple):
                pass 

        if len(filtered_attrs.items()) > 0: 
            print("\t".ljust(indend*4) + '{}'.format(filtered_attrs))

            # run connector if parent node id was stated
            if parent_NodeId != None: 
                # atomic attrs exist on current node -> map to node 
                cypher_statement = neo4jGraphFactory.AddAttributesToNode(parent_NodeId, filtered_attrs, self.timeStamp)
                self.connector.run_cypher_statement(cypher_statement)

        if 'wrappedValue' in info.keys(): 
            print(filtered_attrs['wrappedValue'])





        # query all traversal entities
        children = self.model.traverse(entity, 1)

        # cut the first item
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
        

            for child in children:

                ## check if child is already existing in  graph. otherwise create node
               
                cypher_statement = ''
                cypher_statement = neo4jQueryFactory.GetNodeIdByP21(child.__dict__['id'])
                res = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

                if len(res) == 0:
                    # node doesnt exist yet, continue with creating a new attr node
                    
                    cypher_statement = ''
                    cypher_statement = neo4jGraphFactory.CreateAttributeNode(parent_NodeId, child.__dict__['type'], 'relationshipLabel', self.timeStamp)
                    node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

                    # recursively call the function again but update the node id. It will append the atomic properties and creates the nested child nodes again
                    children = self.getDirectChildren(child, indend + 1, node_id[0])



                elif len(res) == 1:
                    # node already exists, run merge command
                    cypher_statement = ''
                    cypher_statement = neo4jGraphFactory.MergeOnP21(p21_id, child.__dict__['id'], 'relationshipLabel', self.timeStamp)
                    node_id = self.connector.run_cypher_statement(cypher_statement)

                    pass


                elif len(res) > 1: 
                    # node exist multiple times. 
                    raise Exception('Detected nodes with same p21 id. ERROR!')



                
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

