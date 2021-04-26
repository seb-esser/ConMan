
""" package import """
import ifcopenshell

""" file import """
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jGraphFactory import Neo4jGraphFactory
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory
from common_base.ifcMapper import IfcMapper

class IFCp21_MetaGraphGenerator(IfcMapper):
    """
    IfcP21 to neo4j mapper. 
    Translates a given IFC model in P21 encoding into a propertyGraph 
    """

    # constructor
    """ 
    Public constructor for IFCP21_neo4jMapper
    trigger console output while parsing using the ToConsole boolean
    """
    def __init__(self, connector, model_path, ParserConfig): 
       
        
        # try to open the ifc model and load the content into the model variable
        try:
            self.model = ifcopenshell.open(model_path)
        except :
            raise Exception('Unable to open IFC model on given file path')

        # define the label (i.e., the model timestamp)
        my_label = 'ts' + self.model.wrapped_data.header.file_name.time_stamp
        my_label = my_label.replace('-','')
        my_label = my_label.replace(':','')
        self.label = my_label

        # set the connector
        self.connector = connector
       
        # set output 
        self.parserConfig = ParserConfig
        self.printToConsole = False
        self.printToLog = True

        super().__init__()

    # public entry method to generate the graph out of a given IFC model
    def generateGraph(self): 
        # delete entire graph if label already exists
        print('DEBUG INFO: entire graph labeled with >> {} << gets deleted'.format(self.label))
        self.connector.run_cypher_statement('MATCH(n:{}) DETACH DELETE n'.format(self.label))

        print('[IFC_P21 > {} < ]: Generating graph... '.format(self.label))

        # extract model data
        obj_definitions =  self.model.by_type('IfcObjectDefinition')
        obj_relationships = self.model.by_type('IfcRelationship')
        props = self.model.by_type('IfcPropertyDefinition')      

        # parse rooted node + subgraphs
        self.__mapEntities(obj_definitions)

        # parse objectified relationships
        self.__mapObjRelationships(obj_relationships)

        # ToDo: handle IfcPropertyDefinition

        print('[IFC_P21 > {} < ]: Generating graph - DONE. \n '.format(self.label))

    def validateParsingResult(self):
        # ticket_PostEvent-VerifyParsedModel

        # step 1: count entities in IFC model

        # step 2: count number of nodes created in the related graph structure
        # step 2a: identify the graph by its label (i.e., timestamp)
        # step 2b: create a new method in the class neo4jQueryFactory
        # step 2c: implement a suitable cypher statement into the recently created method in neo4jQueryFactory
        # step 2d: run the cypher query using the self.connector.run_cypher_statement() 
        # step 2e: access the database response

        # step 3: compare num_entities from the IFC model with the number of nodes detected in the graph

        # step 4: print the test result to console. 

        pass



    # public entry
    def __mapEntities(self, rootedEntities): 
        # loop over all rooted entities
        for entity in rootedEntities: 
        
            # get some basic data
            info = entity.get_info()
            entityId = info['GlobalId']
            entityType = info['type']

            # neo4j: build rooted node
            cypher_statement = Neo4jGraphFactory.create_primary_node(entityId, entityType, self.label)
            node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')
            
            # get all attrs and children
            self.__getDirectChildren(entity, 0, node_id[0])

    # private recursive function
    def __getDirectChildren(self, entity, indent, parent_NodeId=None): 
        
        if self.printToConsole: 
            print("".ljust(indent*4) + '{}'.format(entity))

        # print atomic attributes: 
        info = entity.get_info()
        p21_id = info['id']
        entityType = info['type']
        # remove type and id from attrDict
        excludeKeys = ['id', 'type']        
        attrs_dict = {key: val for key, val in info.items() if key not in excludeKeys }    
        
        # remove complex traversal attributes
        filtered_attrs = {}
        complex_attrs = []

        # add artifical parameter indicating the P21 entity number. Can be removed in post processing. 
        filtered_attrs['p21_id'] = p21_id
        # remove traverse attrs        
        for key, val in attrs_dict.items():

            # some special tuples that have to be treated differently from pure lists
            special_key_names = ['Coordinates', 'DirectionRatios']
            nestedLists_key_names = ['CoordList', 'segments']
            pdt_key_names = ['PredefinedType']

            # detecting atomic attribute -> map to existing node
            if isinstance(val, str) or isinstance(val, float) or isinstance(val, int) or isinstance(val, bool) : 
                filtered_attrs[key] = val

            elif key in pdt_key_names:
                filtered_attrs[key] = str(val)
            
            # detecting atomic attribute but encapsulated in tuple
            elif isinstance(val, tuple) and key in special_key_names:
                
                for tuple_val in range(len(val)): 
                    cur_key = 'value{}'.format(tuple_val)
                    cur_val = val[tuple_val]
                    # ToDo: numeric issue here!
                    filtered_attrs[cur_key] = filtered_attrs[key] = float("{:.2f}".format(cur_val))
            
            # detecting a list of child entities (again encapsulated as a list)
            elif isinstance(val, tuple) and len(val) > 1 and key not in special_key_names: 

                # reserve suitable names for the relationships between parent and children
                for i in range(len(val)):
                    # append the list item index to the relationship type 
                    rel_type = key + '__listItem_' + str(i)
                    complex_attrs.append(rel_type)
                    
            # detecting a simple child node
            else: 
                if val != None: 
                    complex_attrs.append(key)

        # run the mapping of the detected data. 
        #       filtered_attrs contain atomic attributes, which gets attached as properties at the parent node
        #       complex_attrs  contain all attributes that need sub-nodes. They get zipped with the traverse children afterwards. 

        if len(filtered_attrs.items()) > 0: 
            if self.printToConsole:
                print("\t".ljust(indent*4) + '{}'.format(filtered_attrs))

            # append atomic attrs to current node
            if parent_NodeId != None: 
                # atomic attrs exist on current node -> map to node 
                cypher_statement = Neo4jGraphFactory.add_attributes_by_node_id(parent_NodeId, filtered_attrs,
                                                                               self.label)
                self.connector.run_cypher_statement(cypher_statement)
       
        # query all traversal entities -> subnodes 
        children = self.model.traverse(entity, 1)

        # cut the first item as it is the parent itself
        children = children[1:]

        # combine the detected entities with the corresponding attribute names from 'complex_attrs' list
        complex_childs = set(zip(complex_attrs, children))

        if len(children) == 0:
            pass
        else:        

            for child in complex_childs:

                ## check if child is already existing in the graph. otherwise create new node
               
                cypher_statement = ''
                cypher_statement = neo4jQueryFactory.GetNodeIdByP21(child[1].__dict__['id'], self.label)
                res = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

                if len(res) == 0:
                    # node doesnt exist yet, continue with creating a new attr node
                    
                    cypher_statement = ''
                    cypher_statement = Neo4jGraphFactory.create_secondary_node(parent_NodeId, child[1].__dict__['type'],
                                                                               child[0], self.label)
                    node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

                    # recursively call the function again but update the node id. 
                    # It will append the atomic properties and creates the nested child nodes again
                    children = self.__getDirectChildren(child[1], indent + 1, node_id[0])

                elif len(res) == 1:
                    # node already exists, run merge command

                    cypher_statement = ''
                    cypher_statement = Neo4jGraphFactory.merge_on_p21(p21_id, child[1].__dict__['id'], child[0],
                                                                      self.label)
                    node_id = self.connector.run_cypher_statement(cypher_statement)

                elif len(res) > 1: 
                    # node exist multiple times. 
                    raise Exception('Detected nodes with same p21 id. ERROR!')
                                
        return None

    # public entry
    def __mapObjRelationships(self, objRels): 

        # loop over all relationships
        for entity in objRels: 
        
            # get some basic data
            info = entity.get_info()
            entityId = info['GlobalId']
            entityType = info['type']

            # neo4j: build rooted node
            cypher_statement = Neo4jGraphFactory.create_connection_node(entityId, entityType, self.label)
            node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')
            
            # get all attrs and children
            self.__getDirectChildren(entity, 0, node_id[0])



