
import types
from .neo4jConnector import Neo4jConnector 


class IfcNeo4jMapper:

        
    def __init__(self, myConnector):
        print('Initialized mapper. ')
        self.connector = myConnector
        pass


    

    def mapEntities(self, entities):
        # STEP 1: create all routed entities and add their guids
        for entity in entities:
            print('Creating entity with guid {} in graph...'.format(entity['globalId']))
            # formulate cypher command
            cypher_statement = self.CreateRootedNode(entity['globalId'], entity['type'])
            # run command on database
            response = self.connector.run_cypher_statement(cypher_statement)
           
        return True

    def mapAttributes(self, attributes, parentId):
        
        # get Parent Id
        if isinstance(parentId, str): 
            id = self.connector.run_cypher_statement('MATCH(n) WHERE n.globalId = "{}" RETURN ID(n)'.format(parentId), 'ID(n)')

        else:
            id = entityId


        print(id)   
        ### recursive function that maps all unrooted attributes of a given
        ### entity
        for attr, val in attributes:
            print('{:<15} \t {}'.format(attr, val))
            cypher_statement = ''

            ## top level: either atomic or dict/list

            # --- atomic prop --- 
            """
            Atomic properties are parsed with SET
            """

            if isinstance(val, (int, float, complex, str)):
                attribute = {attr: val}
                print(attribute)
                cypher_statement = self.AddAttributesToRootedNode(entityId, attribute)
                print(cypher_statement)

            # --- dict/list ---
            """ 
            Complex properties get so-called unrooted nodes
            """

            if isinstance(val, dict): # single pValue but referencing to another class
                nodeLabel = val['type']
                parentglobalId = entityId
                
                # create node
                cypher_statement = self.CreateAttributeNode(parentglobalId, nodeLabel, attr )
                # run command on database
                response = self.connector.run_cypher_statement(cypher_statement)
                ID_created = response[0]

                # remote type attr
                exlude = ['type']
                resultset = {key: val for key,val in attributes if key not in exlude}
                
                inner_vals = resultset.items()
                for key, val in inner_vals: 
                    print('{}: \t {}'.format(key, val))
                    # ToDo: Implement parsing

               # refObj = self.DetectReferenceObject(val)


            if isinstance(val, list): # set of pValues
                # dealing with lists
                val_type = 'dictAttr'
                print('-> ListAttr \n')
                i = 1
                for list_val in val:
                    print('-- list val item {}'.format(i))
                    print(list_val)
                    i += 1
                    print('\n')


            # run command on database
            self.connector.run_cypher_statement(cypher_statement)
        print('\n')
                

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def CreateRelationship(self, sourceNodeId, qualifier, type, ref):
        
        match_source  = 'MATCH(s) where ID(s) = {}'.format(sourceNodeId)
        match_target  = 'MATCH(t) where t.globalId = "{}"'.format(ref)
        merge         = 'MERGE (s)-[r.{}]->(t)'.format(type)
        set_qualifier = 'SET r.Qualifier = {}'.format(qualifier)

        return self.BuildMultiStatement([match_source, match_target, merge, set_qualifier])
        

    def CreateRootedNode(self, entityId, entityType):
        create        = 'CREATE(n:{}:rootedNode)'.format(entityType)
        setGuid       = 'SET n.globalId = "{}"'.format(entityId)
        returnID      = 'RETURN ID(n)'
        return self.BuildMultiStatement([create, setGuid, returnID])


    def AddAttributesToRootedNode(self, entityId, attributes):
        match         = 'MATCH(n) WHERE n.globalId = "{}"'.format(entityId)

        for attr, val in attributes.items(): 
            if isinstance(val, str):
                add_param = 'SET n.{} = "{}"'.format(attr, val)
            elif isinstance(val, (int, float, complex)):
                add_param = 'SET n.{} = {}'.format(attr, val)
            else: 
                # ToDo: throw exeption
                print('Do something... ERROR!!')

        returnID         = 'RETURN n'

        return self.BuildMultiStatement([match, add_param, returnID])


    def CreateAttributeNode(self, ParentEntityId, NodeLabel, parentAttrName):
        match          = 'MATCH (p) WHERE p.globalId = "{}"'.format(ParentEntityId)
        create         = 'CREATE (n: {}:attrNode)'.format(NodeLabel)             
        merge          = 'MERGE (p)-[:{}]-> (n)'.format(parentAttrName)
        returnID       = 'RETURN ID(n)'

        #for attr, val in atomicAttrs: 
        #    add_param = 'SET n.{} = {}'.format(attr, val)
        #    cypher_statement = cypher_statement + add_param
                
        return self.BuildMultiStatement([match, create, merge, returnID])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # identifies an ReferenceObject
    def DetectReferenceObject(self, nestedValDict): 
        keys = nestedValDict.keys()
        print(keys)
        if nestedValDict.keys == ['type' , 'ref']:
            return True
        else:
           return False

    # constructs a multi statement cypher command
    def BuildMultiStatement(self, cypherCMDs):
         return ' '.join(cypherCMDs)


    