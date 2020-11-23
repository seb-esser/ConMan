


from pycommon.ifcNetworkXMapper import IfcNetworkXMapper

print('nX mapper')

ifc_initial = './processedModels/spatial_initial.ifc'
ifc_updated = './processedModels/spatial_updated.ifc'

mapper = IfcNetworkXMapper()
model = mapper.loadIfcModel(ifc_initial)
ifc_objDefs = model.by_type('IfcObjectDefinition')
ifc_Rels = model.by_type('IfcRelationship')

for ent in ifc_objDefs: 
	print('{} references:'.format(ent.Name))
	try:
	    print(model.get_traverse(ent))
	except :
	    pass

	print('{} gets referenced by:'.format(ent.Name))
	try:
	    print(model.get_inverse(ent))
	except :
	    pass
	
	print('\n')

for ent in ifc_Rels: 
	print('{} references:'.format(ent.Name))
	try:
	    print(model.get_traverse(ent))
	except :
	    pass

	print('{} gets referenced by:'.format(ent.Name))
	try:
	    print(model.get_inverse(ent))
	except :
	    pass
	
	print('\n')

	# print(ent.get_info())



