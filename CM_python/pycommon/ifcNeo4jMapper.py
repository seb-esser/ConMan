
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
            self.connector.run_cypher_statement(cypher_statement)

        return True

    def mapAttributes(self, attributes, entityId):
        
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
                self.connector.run_cypher_statement(cypher_statement)


                # remote type attr
                exlude = ['type']
                resultset = {key: val for key,val in attributes if key not in exlude}
                
                inner_vals = resultset.items()
                for key, val in inner_vals: 
                    print('{}: \t {}'.format(key, val))
                    # ToDo: Implement parsing

                refObj = self.DetectReferenceObject(val)


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
        cypher_statement = [
            'MATCH(s) where ID(s) = {}'.format(sourceNodeId), 
            'MATCH(t) where t.globalId = "{}"'.format(ref),
            'MERGE (s)-[r.{}]->(t)'.format(type) ,
            'SET r.Qualifier = {}'.format(qualifier)]

        return "".join(str(x) for x in cypher_statement)
        

    def CreateRootedNode(self, entityId, entityType):
        separator = ''
        cypher_statement = [
            'CREATE(n:',
            entityType ,
            ':rootedNode' ,
            '{' ,
            'globalId:"{}'.format(entityId) ,
            '"}' ,
            '); ' ]

        return "".join(str(x) for x in cypher_statement)


    def AddAttributesToRootedNode(self, entityId, attributes):
        cypher_statement = 'MATCH(n) WHERE n.globalId = "{}" ; '.format(entityId)

        for attr, val in attributes.items(): 
            if isinstance(val, str):
                add_param = 'SET n.{} = "{}" '.format(attr, val)
            elif isinstance(val, (int, float, complex)):
                add_param = 'SET n.{} = {} '.format(attr, val)
            else: 
                # ToDo: throw exeption
                print('Do something... ERROR!!')
            cypher_statement = cypher_statement + add_param

        return cypher_statement + ' return n'


    def CreateAttributeNode(self, ParentEntityId, NodeLabel, parentAttrName):
        
        separator = ''
        create = [
            'CREATE(n:',
            NodeLabel ,
            ':attrNode' ,
            ')' ]
        cypher_statement = "".join(str(x) for x in create)

        match = 'MATCH (p) WHERE p.globalId = "{}" ; '.format(ParentEntityId)
        merge = 'MERGE (p)-[:{}]-> (n) '.format(parentAttrName)

        #for attr, val in atomicAttrs: 
        #    add_param = 'SET n.{} = {}'.format(attr, val)
        #    cypher_statement = cypher_statement + add_param
        combined = (match + cypher_statement + merge)

        return combined


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # identifies an ReferenceObject
    def DetectReferenceObject(self, nestedValDict): 
        keys = nestedValDict.keys()
        print(keys)
        if nestedValDict.keys == ['type' , 'ref']:
            return True
        else:
           return False



    