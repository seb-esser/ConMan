
import ifcopenshell

path = './00_sampleData/IFC_stepP21/4x3Bridge/f-bru_enriched_testing_export_select.ifc'

model = ifcopenshell.open(path)

objDefs = model.by_type('IfcFacilityPart')

for entity in objDefs:
	print('{}'.format(entity))
	for key,val in entity.get_info().items():
		print('{} \t {} \t {}'.format(key, val, type(val) ))
	print('\n')



