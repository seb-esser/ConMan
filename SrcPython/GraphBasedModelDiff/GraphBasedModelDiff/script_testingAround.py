
import ifcopenshell

#path = './00_sampleData/IFC_stepP21/4x3Bridge/f-bru_enriched_testing_export_select.ifc'

#model = ifcopenshell.open(path)

#objDefs = model.by_type('IfcFacilityPart')

#for entity in objDefs:
#	print('{}'.format(entity))
#	for key,val in entity.get_info().items():
#		print('{} \t {} \t {}'.format(key, val, type(val) ))
#	print('\n')


from neo4j_middleware.neo4jGraphFactory import neo4jGraphFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector


connector = Neo4jConnector(writeToConsole=False)
connector.connect_driver()

path = './00_sampleData/IFC_stepP21/Beam_extrudedGeom/beam-extruded-solid_initial.ifc'
ts = "testts"
cy = 'MATCH (n:{}) DETACH DELETE n'.format(ts)
connector.run_cypher_statement(cy)


model = ifcopenshell.open(path)
cartesianPtList2D = model.by_type('IfcCartesianPointList2D')[0]

cy = neo4jGraphFactory.CreateAttributeNode_wouParent(cartesianPtList2D.get_info()['type'], ts)
id_cPtL = connector.run_cypher_statement(cy, 'ID(n)')[0]

for key, val in cartesianPtList2D.get_info().items():

	print('{:<8} \t {}'.format(key, type(val) ))

	if isinstance(val, tuple): 
		if len(val) > 1:
			print('-> LIST node is required. ')
			cy = neo4jGraphFactory.CreateListNode(id_cPtL, str(key), ts)
			lst = connector.run_cypher_statement(cy, 'ID(n)')[0]

			i = 0
			for nVal in val: 
				print('\t\t Val1: {:.2f} \t Val2: {:.2f} \t'.format(nVal[0], nVal[1]))
				cy = neo4jGraphFactory.CreateListItemNode(lst, i, ts)
				itm = connector.run_cypher_statement(cy, 'ID(n)')[0]
				
				attrs = {}
				attrs['ItemValue1'] = nVal[0]
				attrs['ItemValue2'] = nVal[1]				
				cy = neo4jGraphFactory.AddAttributesToNode(itm, attrs, ts)

				connector.run_cypher_statement(cy)
				i = i+1

		else:
			print('\t easy tuple')



connector.disconnect_driver()
