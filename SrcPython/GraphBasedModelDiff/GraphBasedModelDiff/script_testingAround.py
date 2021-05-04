import ifcopenshell

from neo4j_middleware.Neo4jGraphFactory import Neo4jGraphFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector

# path = './00_sampleData/IFC_stepP21/4x3Bridge/f-bru_enriched_testing_export_select.ifc'
# model = ifcopenshell.open(path)
# objDefs = model.by_type('IfcFacilityPart')
# for entity in objDefs:
# 	print('{}'.format(entity))
# 	for key,val in entity.get_info().items():
# 		print('{} \t {} \t {}'.format(key, val, type(val) ))
# 	print('\n')

connector = Neo4jConnector(writeToConsole=False)
connector.connect_driver()

path = './00_sampleData/IFC_stepP21/Beam_extrudedGeom/beam-extruded-solid_initial.ifc'
ts = "testts"
cy = 'MATCH (n:{}) DETACH DELETE n'.format(ts)
connector.run_cypher_statement(cy)

model = ifcopenshell.open(path)
cartesianPtList2D = model.by_type('IfcCartesianPointList2D')[0]
cpl_type = cartesianPtList2D.get_info()['type']
cy = Neo4jGraphFactory.create_secondary_node(parent_id=None, entity_type=cpl_type, rel_type=None, timestamp=ts)
id_cPtL = connector.run_cypher_statement(cy, 'ID(n)')[0]

for key, val in cartesianPtList2D.get_info().items():

    print('{:<8} \t {}'.format(key, type(val)))

    if isinstance(val, tuple):
        if len(val) > 1:
            print('-> LIST node is required. ')
            cy = Neo4jGraphFactory.create_list_node(id_cPtL, str(key), ts)
            lst = connector.run_cypher_statement(cy, 'ID(n)')[0]

            i = 0
            for nVal in val:
                print('\t\t Val1: {:.2f} \t Val2: {:.2f} \t'.format(nVal[0], nVal[1]))
                cy = Neo4jGraphFactory.create_list_item_node(lst, i, ts)
                itm = connector.run_cypher_statement(cy, 'ID(n)')[0]

                attrs = {'ItemValue1': nVal[0], 'ItemValue2': nVal[1]}
                cy = Neo4jGraphFactory.add_attributes_by_node_id(itm, attrs, ts)

                connector.run_cypher_statement(cy)
                i = i + 1

        else:
            print('\t easy tuple')

connector.disconnect_driver()
