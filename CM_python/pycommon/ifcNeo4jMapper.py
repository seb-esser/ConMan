
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

    def mapAttributes(self, attributes, entityId, isRecursionEntry):
        
        print('is recursion entry? \t {}'.format(isRecursionEntry))

        print(attributes)

        ### recursive function that maps all unrooted attributes of a given
        ### entity
        for attr, val in attributes:
            print('{:<15} \t {}'.format(attr, val))
            cypher_statement = ''

            if attr == 'ref': 
                # build relationship
                print('{} with value {} has to be processed as a relationship.'.format(attr, val))

                print('-> parse ref as relationship')
                # parse next attribute
                continue

            if attr != 'globalId' and attr != 'type' and isRecursionEntry == True: # exclude the globalId and type attr as this was already parsed

                if isinstance(val, dict):
                    # dealing with dicts
                    val_type = 'dictAttr'
                    print('-> Do a recursive call here!')
                    
                    inner_vals = val.items()

                    self.mapAttributes(inner_vals, entityId, False) 

                if isinstance(val, list):
                    # dealing with lists
                    val_type = 'dictAttr'
                    print('-> Do a recursive call here!')
                    
                    self.mapAttributes(inner_vals, entityId, False) 


                if isinstance(val, str): 
                    val_type = 'stringAttr'
                    print('-> {} with value {} has to be processed as a string attr'.format(attr, val))
                    cypher_statement = 'Match(n) where n.globalId="{}" set n.{} = "{}" return n'.format(entityId, attr, val)
                    print(cypher_statement)


                if isinstance(val, (int, float, complex)):
                    val_type = 'numericType'
                    print('-> {} with value {} has to be processed as a NUMERIC attr'.format(attr, val))
                    cypher_statement = 'Match(n) where n.globalId="{}" set n.{} = {} return n'.format(entityId, attr, val)
                    print(cypher_statement)

                # run command on database
                self.connector.run_cypher_statement(cypher_statement)
        print('\n')
                

    def parseRelationship(self, sourceNodeId, qualifier, type, ref):
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






