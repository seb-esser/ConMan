
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

            if isinstance(val, dict):
                # dealing with dicts
                val_type = 'dictAttr'
                print('-> DictAttr')
                    
                inner_vals = val.items()


            if isinstance(val, list):
                # dealing with lists
                val_type = 'dictAttr'
                print('-> ListAttr')
                

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
            ')' ]

        return "".join(str(x) for x in cypher_statement)


    def AddAttributesToRootedNode(self, entityId, attributes):
        cypher_statement = 'MATCH(n) WHERE n.globalId = "{}" '.format(entityId)

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


    def CreateAttributeNode(self, ParentEntityId, attrName,  attributes):
        separator = ''
        create = [
            'CREATE(n:',
            attrName ,
            ':attrNode' ,
            ')' ]
        cypher_statement = "".join(str(x) for x in create)

        for attr, val in attributes: 
            add_param = 'SET n.{} = {}'.format(attr, val)
            cypher_statement = cypher_statement + add_param

        return cypher_statement






