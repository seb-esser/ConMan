
import types
from .neo4jConnector import Neo4jConnector 
from .IfcRelHelper.InverseAttrDetector import InverseAttrDectector
from .IfcRelHelper.IfcRelCommon import IfcRelCommon

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
            response = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

            # extract owner history and merge with correct owner history
            # (assuming it already exists!)
            try:
                parent_owner_history = entity['ownerHistory']
                OH_guid = parent_owner_history['ref']
                cypher_statement = ''
                cypher_statement = self.MergeRootedNodeWithOwnerHistory(OH_guid, response[0])
                response = self.connector.run_cypher_statement(cypher_statement, 'ID(me)')
            except :
                pass
            
        return True

    def mapProperties(self, entityGlobalId, attributes):
        # get node id of parent
        root_node_id = self.connector.run_cypher_statement('MATCH(n) WHERE n.globalId = "{}" RETURN ID(n)'.format(entityGlobalId), 'ID(n)')

        root_node_id = root_node_id[0]



        # remove type and globalId from entity properties
        exlude = ['globalId', 'type', 'ownerHistory']
        reduced_properties = {key: val for key,val in attributes if key not in exlude}
    
        # reduced attributes
        reduced_attributes = reduced_properties.items()

        for pName, pVal in reduced_attributes: 
            self._MapAttribute(pName, pVal, root_node_id)


    def _MapAttribute(self, pName, pVal, parentId):
            
        #inverseAttrDetector = InverseAttrDectector()
        #invAttr = inverseAttrDetector.IsInverseAttr(pName)

        #if invAttr:
        #    print('detected inverse attribute')

        objectified_rel_list = self.getObjectifiedRels()


        # --- atomic prop ---
        if isinstance(pVal, (int, float, complex, str)):
            attribute = {pName: pVal}
            print(attribute)
            cypher_statement = self.AddAttributesToNode(parentId, attribute)
            self.connector.run_cypher_statement(cypher_statement)                
            return None

        # --- dict/list ---
        if isinstance(pVal, dict): # single pValue but referencing to another class
                
            # STEP 1: create new node, get its Id and merge with parent
            # using the 'type' value
            nodeLabel = pName
            
            child_type = 'undefinedRel'
            try:
                 child_type = pVal['type'] 
            except :
                pass
                       
            # STEP 2: check if property is an inverse attribute referencing an
            # objectified relationship
            if child_type in objectified_rel_list:
                # found an objectified relationship!
                print(pVal)
                
                return
                # build_refs_from_to = self.ParseObjectifiedRelationship(pVal)
                           

            cypher_statement = self.CreateAttributeNode(parentId, nodeLabel, child_type)
            current_parent = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

            # STEP 3: take the new parent and parse the inner dict values:
            for pName,pInnerVal in pVal.items():
                self._MapAttribute(pName, pInnerVal, current_parent[0])                          
            return None

        if isinstance(pVal, list): # set of pValues

            for list_val in pVal:
                # loop over all list items and insert them into the graph
                # list_val is a dict in itself most of the time!

                child_type = 'undefinedRel'
                try:
                     child_type = pVal['type'] 
                except :
                    pass
                if child_type in objectified_rel_list:
                    # found an objectified relationship!
                    print(list_val) 
                    return 
                    # build_refs_from_to =
                    # self.ParseObjectifiedRelationship(pName, pVal, parentId)
                else:
                    self._MapAttribute(pName, list_val, parentId)



    def ParseObjectifiedRelationship(self, pName, pVal, sourceNodeId):

        # STEP 1: Parse all attributes

        # STEP 2: Store all new relationships in a suitable dict: {rel_label:
        # [fromNodeID -> toNodeID] }


        return 'doSomething'
                   
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CreateRelationship(self, sourceNodeId, qualifier, type, ref):
        match_source = 'MATCH(s) where ID(s) = {}'.format(sourceNodeId)
        match_target = 'MATCH(t) where t.globalId = "{}"'.format(ref)
        merge = 'MERGE (s)-[r.{}]->(t)'.format(type)
        set_qualifier = 'SET r.Qualifier = {}'.format(qualifier)

        return self.BuildMultiStatement([match_source, match_target, merge, set_qualifier])
        

    def CreateRootedNode(self, entityId, entityType):
        create = 'CREATE(n:{}:rootedNode)'.format(entityType)
        setGuid = 'SET n.globalId = "{}"'.format(entityId)
        setEntityType = 'SET n.entityType = "{}"'.format(entityType)
        returnID = 'RETURN ID(n)'
        return self.BuildMultiStatement([create, setGuid, setEntityType, returnID])


    def AddAttributesToNode(self, nodeId, attributes):
        match = 'MATCH(n) WHERE ID(n) = {}'.format(nodeId)

        for attr, val in attributes.items(): 
            if isinstance(val, str):
                add_param = 'SET n.{} = "{}"'.format(attr, val)
            elif isinstance(val, (int, float, complex)):
                add_param = 'SET n.{} = {}'.format(attr, val)
            else: 
                # ToDo: throw exeption
                print('Do something... ERROR!!')

        returnID = 'RETURN n'

        return self.BuildMultiStatement([match, add_param, returnID])


    def CreateAttributeNode(self, ParentId, NodeLabel, RelationshipLabel):
        match = 'MATCH (p) WHERE ID(p) = {}'.format(ParentId)
        create = 'CREATE (n: {}:attrNode)'.format(NodeLabel)             
        merge = 'MERGE (p)-[:{}]->(n)'.format(RelationshipLabel)
        returnID = 'RETURN ID(n)'

        #for attr, val in atomicAttrs:
        #    add_param = 'SET n.{} = {}'.format(attr, val)
        #    cypher_statement = cypher_statement + add_param
                
        return self.BuildMultiStatement([match, create, merge, returnID])

    def MergeRootedNodeWithOwnerHistory(self, ownerHistoryGuid, myNodeId):
        match = 'MATCH (p) WHERE p.globalId = "{}"'.format(ownerHistoryGuid)
        matchOwn = 'MATCH (me) WHERE ID(me) = {}'.format(myNodeId)
        merge = 'MERGE (me)-[:{}]->(p)'.format('IfcOwnerHistory')
        returnID = 'RETURN ID(me)'

        return self.BuildMultiStatement([match, matchOwn, merge, returnID])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - -
    def getObjectifiedRels(self): 
        return [# IfcRelAssigns derived
            "IfcRelAssignsToActor",
            "IfcRelAssignsToControl",
            "IfcRelAssignsToGroup",
            "IfcRelAssignsToProcess",
            "IfcRelAssignsToProduct",
            "IfcRelAssignsToResource",


            # IfcRelAssociates derived
            "IfcRelAssociatesApproval",
            "IfcRelAssociatesClassification",
            "IfcRelAssociatesConstraint",
            "IfcRelAssociatesDocument",
            "IfcRelAssociatesLibrary",
            "IfcRelAssociatesMaterial",
            "IfcRelAssociatesProfileDef",

            # IfcRelConnects derived
            "IfcRelConnectsElements",
            "IfcRelConnectsPortToElement",
            "IfcRelConnectsPorts",
            "IfcRelConnectsStructuralActivity",
            "IfcRelConnectsStructuralMember",
            "IfcRelContainedInSpatialStructure",
            "IfcRelCoversBldgElements",
            "IfcRelCoversSpaces",
            "IfcRelFillsElement",
            "IfcRelFlowControlElements",
            "IfcRelInterferesElements",
            "IfcRelPositions",
            "IfcRelReferencedInSpatialStructure",
            "IfcRelSequence",
            "IfcRelServicesBuildings",
            "IfcRelSpaceBoundary",
            "IfcRelDeclares",

            # IfcRelDecomposes derived
            "IfcRelAggregates",
            "IfcRelNests",
            "IfcRelProjectsElement",
            "IfcRelVoidsElement",


            # IfcRelDefines derived
            "IfcRelDefinesByObject",
            "IfcRelDefinesByProperties",
            "IfcRelDefinesByTemplate",
            "IfcRelDefinesByType",

            "IfcRelAggegrates",
            "IfcRelCrosses"]


