


from pycommon.ifcNetworkXMapper import IfcNetworkXMapper

print('nX mapper')

ifc_initial = './processedModels/spatial_initial.ifc'
ifc_updated = './processedModels/spatial_updated.ifc'

mapper_initial = IfcNetworkXMapper()
mapper_initial.loadIfcModel(ifc_initial)

mapper_updated = IfcNetworkXMapper()
mapper_updated.loadIfcModel(ifc_updated)

print('basic quanitites of initial model:')
mapper_initial.getBasicMetaDataFromModel()
print('basic quanitites of updated model:')
mapper_updated.getBasicMetaDataFromModel()






#for ent in ifc_objDefs: 
#	print('{} references:'.format(ent.Name))
#	try:
#	    print(model.get_traverse(ent))
#	except :
#	    pass

#	print('{} gets referenced by:'.format(ent.Name))
#	try:
#	    print(model.get_inverse(ent))
#	except :
#	    pass
	
#	print('\n')

#for ent in ifc_objDefs: 
#	print('{} references:'.format(ent))
#	try:
#		references = model.traverse(ent, max_levels=1)
#		for ref in references:
#			print(ref.Name)
#	except :
#	    pass

#	print('{} gets referenced by:'.format(ent))
#	try:
#		references = model.traverse(ent, max_levels=1)
#		for ref in references:
#			print(ref.Name)
#	except :
#	    pass
	
#	print('\n')

#	# print(ent.get_info())



