import ifcopenshell


model_init = ifcopenshell.open('./00_sampleData/IFC_stepP21/solibri_example/pretty_SolibriBuilding.ifc')

for inst in model_init:
    p21_id = inst.get_info()['id']
