def relSwitcher(rel):
    relName = rel.Name
    switcher ={
       # "IfcRelAssigns": "asdf",
        "IfcRelAssignsToActor": "adf",
        "IfcRelAssignsToControl": "adf",
        "IfcRelAssignsToGroup": "adf",
        "IfcRelAssignsToProcess": "adf",
        "IfcRelAssignsToProduct": "asdf",
        "IfcRelAssignsToResource": "asdf",


       # "IfcRelAssociates": "asdefr",
        "IfcRelAssociatesApproval": "asdefr",
        "IfcRelAssociatesClassification": "asdefr",
        "IfcRelAssociatesConstraint": "asdefr",
        "IfcRelAssociatesDocument": "asdefr",
        "IfcRelAssociatesLibrary": "asdefr",
        "IfcRelAssociatesMaterial": "asdefr",
        "IfcRelAssociatesProfileDef": "asdefr",


        # "IfcRelConnects": "adf",
        "IfcRelConnectsElements": "asdefr",
        "IfcRelConnectsPortToElement": "asdefr",
        "IfcRelConnectsPorts": "asdefr",
        "IfcRelConnectsStructuralActivity": "adsf",
        "IfcRelConnectsStructuralMember": "adsf",
        "IfcRelContainedInSpatialStructure": "adsf",
        "IfcRelCoversBldgElements": "adsf",
        "IfcRelCoversSpaces": "adsf",
        "IfcRelFillsElement": "adsf",
        "IfcRelFlowControlElements": "adsf",
        "IfcRelInterferesElements": "adsf",
        "IfcRelPositions": "adsf",
        "IfcRelReferencedInSpatialStructure": "adsf",
        "IfcRelSequence": "adsf",
        "IfcRelServicesBuildings": "adsf",
        "IfcRelSpaceBoundary": "adsf",

        # "IfcRelDeclares": "asdf",

        # "IfcRelDecomposes": "adf",

        # "IfcRelDefines": "asdf",

        # "IfcRelAggegrates": mapRelAggregates(rel),
        # "IfcRelCrosses": 2
    }
    return "mappingJSONforRelationship"


def mapRelAggregates(rel):
    return "mappingJSON"



