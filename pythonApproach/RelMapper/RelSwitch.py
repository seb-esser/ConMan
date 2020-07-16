def relSwitcher(rel):
    relName = rel.Name
    switcher = {
        # IfcRelAssigns derived
        "IfcRelAssignsToActor": "adf",
        "IfcRelAssignsToControl": "adf",
        "IfcRelAssignsToGroup": "adf",
        "IfcRelAssignsToProcess": "adf",
        "IfcRelAssignsToProduct": "asdf",
        "IfcRelAssignsToResource": "asdf",


        # IfcRelAssociates derived
        "IfcRelAssociatesApproval": "asdefr",
        "IfcRelAssociatesClassification": "asdefr",
        "IfcRelAssociatesConstraint": "asdefr",
        "IfcRelAssociatesDocument": "asdefr",
        "IfcRelAssociatesLibrary": "asdefr",
        "IfcRelAssociatesMaterial": "asdefr",
        "IfcRelAssociatesProfileDef": "asdefr",


        # IfcRelConnects derived
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


        "IfcRelDeclares": "asdf",


        # IfcRelDecomposes derived
        "fcRelAggregates": "asdf",
        "IfcRelNests": "asdf",
        "IfcRelProjectsElement": "asdf",
        "IfcRelVoidsElement": "asdf",


        # IfcRelDefines derived
        "IfcRelDefinesByObject": "asdf",
        "IfcRelDefinesByProperties": "asdf",
        "IfcRelDefinesByTemplate": "asdf",
        "IfcRelDefinesByType": "asdf"


        # "IfcRelAggegrates": mapRelAggregates(rel),
        # "IfcRelCrosses": 2
    }
    return switcher(relName)


def mapRelAggregates(rel):
    return "mappingJSON"



