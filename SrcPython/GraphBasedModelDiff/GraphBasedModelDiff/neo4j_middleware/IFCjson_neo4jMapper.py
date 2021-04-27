
""" package import """ 
import types

""" class import """

from .neo4jConnector import Neo4jConnector 
from .IfcRelHelper.InverseAttrDetector import InverseAttrDectector
from .IfcRelHelper.IfcObjRelCacher import IfcObjRelCacher, Rel
from common_base.ifcMapper import IfcMapper
from .Neo4jQueryUtilities import Neo4jQueryUtilities as neo4jUtils
from .Neo4jGraphFactory import Neo4jGraphFactory as factory


class IfcJsonNeo4jMapper(IfcMapper):
        
    def __init__(self, myConnector, timestamp):
        self.connector = myConnector
        self.RelCacherList = []
        self.timeStamp = timestamp
        super().__init__()


    def mapEntities(self, entities):
        # STEP 1: create all routed entities and add their guids
        for entity in entities:
            print('Creating entity with guid {} in graph...'.format(entity['globalId']))
            # formulate cypher command
            # cypher_statement = self.CreateRootedNode(entity['globalId'], entity['type'])
            cypher_statement = factory.create_primary_node(entity['globalId'], entity['type'], self.timeStamp)
            # run command on database
            response = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

            # extract owner history and merge with correct owner history
            # (assuming it already exists!)
            try:
                parent_owner_history = entity['ownerHistory']
                OH_guid = parent_owner_history['ref']
                cypher_statement = ''
                cypher_statement = factory.merge_rooted_node_with_owner_history(OH_guid, response[0], self.timeStamp)
                response = self.connector.run_cypher_statement(cypher_statement, 'ID(me)')
            except :
                pass
            
        return True

    def mapProperties(self, entityGlobalId, attributes):
        # get node id of parent
        root_node_id = self.connector.run_cypher_statement('MATCH(n:{}) WHERE n.globalId = "{}" RETURN ID(n)'.format(self.timeStamp, entityGlobalId), 'ID(n)')

        root_node_id = root_node_id[0]


        # remove type and globalId from entity properties
        exlude = ['globalId', 'type', 'ownerHistory']
        reduced_properties = {key: val for key,val in attributes if key not in exlude}
    
        # reduced attributes
        reduced_attributes = reduced_properties.items()

        for pName, pVal in reduced_attributes: 
            self._MapAttribute(pName, pVal, root_node_id)

    def _MapAttribute(self, pName, pVal, parentId):
            
        objectified_rel_list = self.getObjectifiedRels()


        # --- atomic prop ---
        if isinstance(pVal, (int, float, complex, str)):
            attribute = {pName: pVal}
            print(attribute)
            cypher_statement = factory.add_attributes_by_node_id(parentId, attribute, self.timeStamp)
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
                relCache = IfcObjRelCacher(child_type, pVal['globalId'], pVal['ownerHistory']['ref'])
                self.RelCacherList.append(relCache)
                # reduce pVal:
                exlude = ['globalId', 'type', 'ownerHistory']
                reduced_properties = {key: val for key,val in pVal.items() if key not in exlude}

                # try to catch all relationships stored within reduced_pVal
                for nestedRelName, nestedRelVal in reduced_properties.items():
                    print('{}:'.format(nestedRelName))

                    # list or dict?
                    if isinstance(nestedRelVal, dict):
                         # print('\t{}'.format(nestedRelVal))
                         rel = Rel(nestedRelName, pName, nestedRelVal['ref'])
                         relCache.AddOutgoingRel(rel)

                    elif isinstance(nestedRelVal, list):
                        for target in nestedRelVal:
                            # print('\t{}'.format(target))
                            rel = Rel(nestedRelName, pName, target['ref'])
                            relCache.AddOutgoingRel(rel)

                self.RelCacherList.append(relCache)
                return

            cypher_statement = factory.create_secondary_node(parentId, nodeLabel, child_type, self.timeStamp)
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

    def mapObjectifiedRelationships(self):
        unsorted = self.RelCacherList
        # unify the objRels by guids

        all_unsorted_guids = self.getGuidsFromList(unsorted)
        sorted_guids = [] 
        
        # unify list
        for i in all_unsorted_guids: 
            if i not in sorted_guids: 
                sorted_guids.append(i) 

        # add rels to sorted_rel if not added yet 
        sorted_rels = []
        for i in unsorted:            
            try:
                already_added_guids = self.getGuidsFromList(sorted_rels)
            except :
                already_added_guids = []
           
            if i.globalId in sorted_guids and i.globalId not in already_added_guids:
                sorted_rels.append(i)

        for objRel in sorted_rels:
            # print('{} -> {}'.format(objRel.globalId, objRel.RelType))
            cypher_statement = factory.create_connection_node(objRel.globalId, objRel.RelType, self.timeStamp)
            nodeId = self.connector.run_cypher_statement(cypher_statement, 'ID(n)')

            for outs in objRel.outgoing_Rels:                
                # print('\t type: {} \t ref: {}'.format(outs.type, outs.target_guid))
                cypher_statement = factory.merge_con_with_primary_node(objRel.globalId, outs.target_guid,
                                                                       outs.type_from_rel_to_node, outs.inverseType,
                                                                       self.timeStamp)
                self.connector.run_cypher_statement(cypher_statement)

        return 'doSomething'
            
    def getGuidsFromList(self, rel_list):
        returnList = []
        for relationship in rel_list:
            returnList.append(relationship.globalId)
        return returnList


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # identifies an ReferenceObject
    def DetectReferenceObject(self, nestedValDict): 
        keys = nestedValDict.keys()
        print(keys)
        if nestedValDict.keys == ['type' , 'ref']:
            return True
        else:
           return False

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

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


