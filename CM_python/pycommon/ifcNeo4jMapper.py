
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

    def mapProperties(self, entityGlobalId, attributes):
        # get node id of parent
        root_node_id = self.connector.run_cypher_statement('MATCH(n) WHERE n.globalId = "{}" RETURN ID(n)'.format(entityGlobalId), 'ID(n)')

        root_node_id = root_node_id[0]

        # remove type and globalId from entity properties
        exlude = ['globalId', 'type']
        reduced_properties = {key: val for key,val in attributes if key not in exlude}
    
        # reduced attributes
        reduced_attributes = reduced_properties.items()

        for pName, pVal in reduced_attributes: 
            self._MapAttribute(pName, pVal, root_node_id)


    def _MapAttribute(self, pName, pVal, parentId):
        
            # --- atomic prop ---            
            if isinstance(pVal, (int, float, complex, str)):
                attribute = {pName: pVal}
                print(attribute)
                cypher_statement = self.AddAttributesToNode(parentId, attribute)
                self.connector.run_cypher_statement(cypher_statement)                
                return None

            # --- dict/list ---
            if isinstance(pVal, dict): # single pValue but referencing to another class
                
                # STEP 1: create new node, get its Id and merge with parent using the 'type' value
                nodeLabel = pName

                # Issue: not every property has a type
                if 'type' in pVal:
                    relationship_label = pVal['type']
                else:
                    relationship_label = 'undefinedRel'
                cypher_statement = self.CreateAttributeNode(parentId, nodeLabel, relationship_label)
                current_parent = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')
                
                # STEP 2: remove the type property from the inner dict (already used to label the node
                #exlude = ['type']
                #reduced_properties = {key:val for key,val in pVal if key not in exlude}
                #reduced_attributes = reduced_properties.items()
                #reduced_attributes = pVal

                # STEP 3: take the new parent and parse the inner dict values:
                for pName,pInnerVal in pVal.items():
                    self._MapAttribute(pName, pInnerVal, current_parent[0])                          
                return None

            if isinstance(pVal, list): # set of pValues
                for list_val in pVal:
                    # loop over all list items and insert them into the graph
                    # list_val is a dict in itself most of the time!
                    self._MapAttribute(pName, list_val, parentId)

                   
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


    def AddAttributesToNode(self, nodeId, attributes):
        match         = 'MATCH(n) WHERE ID(n) = {}'.format(nodeId)

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


    def CreateAttributeNode(self, ParentId, NodeLabel, RelationshipLabel):
        match          = 'MATCH (p) WHERE ID(p) = {}'.format(ParentId)
        create         = 'CREATE (n: {}:attrNode)'.format(NodeLabel)             
        merge          = 'MERGE (p)-[:{}]->(n)'.format(RelationshipLabel)
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


    