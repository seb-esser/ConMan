
""" package import """
import ifcopenshell

""" file import """
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jGraphFactory import neo4jGraphFactory
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory
from common_base.ifcMapper import IfcMapper

class IFCp21_neo4jMapper(IfcMapper):
    """
    IfcP21 to neo4j mapper. 
    Translates a given IFC model in P21 encoding into a propertyGraph 
    """

    # constructor
    """ 
    Public constructor for IFCP21_neo4jMapper
    trigger console output while parsing using the ToConsole boolean
    """
    def __init__(self, myConnector, timestamp, my_model, ToConsole = False, ToLog = True): 
       
        self.connector = myConnector
        self.timeStamp = timestamp
        self.model = my_model
        self.printToConsole = ToConsole
        self.printToLog = ToLog
        super().__init__()

    # public entry
    def mapEntities(self, rootedEntities): 
        # loop over all rooted entites 
        for entity in rootedEntities: 
        
            # get some basic data
            info = entity.get_info()
            entityId = info['GlobalId']
            entityType = info['type']

            # neo4j: build rooted node
            cypher_statement = neo4jGraphFactory.CreateRootedNode(entityId, entityType, self.timeStamp)
            node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')
            
            # get all attrs and children
            self.getDirectChildren(entity, 0, node_id[0])

    # private recursive function
    def getDirectChildren(self, entity, indent, parent_NodeId=None): 
        
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

            # detecting atomic attribute -> map to existing node
            if isinstance(val, str) or isinstance(val, float) or isinstance(val, int) or isinstance(val, bool) : 
                filtered_attrs[key] = val
            
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
                cypher_statement = neo4jGraphFactory.AddAttributesToNode(parent_NodeId, filtered_attrs, self.timeStamp)
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
                cypher_statement = neo4jQueryFactory.GetNodeIdByP21(child[1].__dict__['id'], self.timeStamp)
                res = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

                if len(res) == 0:
                    # node doesnt exist yet, continue with creating a new attr node
                    
                    cypher_statement = ''
                    cypher_statement = neo4jGraphFactory.CreateAttributeNode(parent_NodeId, child[1].__dict__['type'], child[0], self.timeStamp)
                    node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

                    # recursively call the function again but update the node id. 
                    # It will append the atomic properties and creates the nested child nodes again
                    children = self.getDirectChildren(child[1], indent + 1, node_id[0])

                elif len(res) == 1:
                    # node already exists, run merge command

                    cypher_statement = ''
                    cypher_statement = neo4jGraphFactory.MergeOnP21(p21_id, child[1].__dict__['id'], child[0], self.timeStamp)
                    node_id = self.connector.run_cypher_statement(cypher_statement)

                elif len(res) > 1: 
                    # node exist multiple times. 
                    raise Exception('Detected nodes with same p21 id. ERROR!')
                                
        return children

    # public entry
    def mapObjRelationships(self, objRels): 

        # loop over all relationships
        for entity in objRels: 
        
            # get some basic data
            info = entity.get_info()
            entityId = info['GlobalId']
            entityType = info['type']

            # neo4j: build rooted node
            cypher_statement = neo4jGraphFactory.CreateObjectifiedRelNode(entityId, entityType, self.timeStamp)
            node_id = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')
            
            # get all attrs and children
            self.getDirectChildren(entity, 0, node_id[0])



