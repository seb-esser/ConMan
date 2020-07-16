def relSwitcher(rel):

    switcher = {
        # IfcRelAssigns derived
        "IfcRelAssignsToActor": map_IfcRelAssignsToActor(rel),
        "IfcRelAssignsToControl": map_IfcRelAssignsToControl(rel),
        "IfcRelAssignsToGroup": map_IfcRelAssignsToGroup(rel),
        "IfcRelAssignsToProcess": map_IfcRelAssignsToProcess(rel),
        "IfcRelAssignsToProduct": map_IfcRelAssignsToProduct(rel),
        "IfcRelAssignsToResource": map_IfcRelAssignsToResource(rel),


        # IfcRelAssociates derived
        "IfcRelAssociatesApproval": map_IfcRelAssociatesApproval(rel),
        "IfcRelAssociatesClassification": map_IfcRelAssociatesClassification(rel),
        "IfcRelAssociatesConstraint": map_IfcRelAssociatesConstraint(rel),
        "IfcRelAssociatesDocument": map_IfcRelAssociatesDocument(rel),
        "IfcRelAssociatesLibrary": map_IfcRelAssociatesLibrary(rel),
        "IfcRelAssociatesMaterial": map_IfcRelAssociatesMaterial(rel),
        "IfcRelAssociatesProfileDef": map_IfcRelAssociatesProfileDef(rel),


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

    rel_name = rel.Name
    return switcher(rel_name)

# map RelAssigns
def map_IfcRelAssignsToActor(rel):
    return "mappingJSON"

def map_IfcRelAssignsToControl(rel):
    return "mappingJSON"

def map_IfcRelAssignsToGroup(rel):
    return "mappingJSON"

def map_IfcRelAssignsToProcess(rel):
    return "mappingJSON"

def map_IfcRelAssignsToProduct(rel):
    return "mappingJSON"

def map_IfcRelAssignsToResource(rel):
    return "mappingJSON"

# map RelAssociates

def map_IfcRelAssociatesApproval(rel):
    return "mappingJSON"

def map_IfcRelAssociatesClassification(rel):
    return "mappingJSON"

def map_IfcRelAssociatesConstraint(rel):
    return "mappingJSON"

def map_IfcRelAssociatesDocument(rel):
    return "mappingJSON"

def map_IfcRelAssociatesLibrary(rel):
    return "mappingJSON"

def map_IfcRelAssociatesMaterial(rel):
    return "mappingJSON"

def map_IfcRelAssociatesProfileDef(rel):
    return "mappingJSON"





