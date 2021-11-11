import ifcopenshell

model_init = ifcopenshell.open('./00_sampleData/IFC_stepP21/solibri_example/pretty_SolibriBuilding.ifc')
model_updated = ifcopenshell.open('./00_sampleData/IFC_stepP21/solibri_example/pretty_SolibriBuilding-modified.ifc')

entities_init = 0
for elem in model_init:
    entities_init += 1


entities_updt = 0
for elem in model_updated:
    entities_updt += 1

print('Entities total - INIT:{}'.format(entities_init))
print('Entities total - UPDT:{}'.format(entities_updt))

# rooted entities

rooted_init = model_init.by_type("IfcObjectDefinition")
rooted_updated = model_updated.by_type("IfcObjectDefinition")
objRels_init = model_init.by_type("IfcRelationship")
objRels_updated = model_updated.by_type("IfcRelationship")

print("ObjectDefinitions - INIT: {}".format(len(rooted_init)))
print("ObjectDefinitions - UPDT: {}".format(len(rooted_updated)))

print("Relationships - INIT: {}".format(len(objRels_init)))
print("Relationships - UPDT: {}".format(len(objRels_updated)))
