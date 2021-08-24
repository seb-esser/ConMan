import ifcopenshell

from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector

model_init = ifcopenshell.open('./00_sampleData/IFC_stepP21/solibri_example/pretty_SolibriBuilding.ifc')
ts_init = "ts20121017T152740"

# db connection
connector = Neo4jConnector()
connector.connect_driver()

non_created_entities = []

for inst in model_init:
    p21_id = inst.get_info()['id']
    cy = Neo4jQueryFactory.get_nodeId_byP21(p21_id, ts_init)
    node_id = connector.run_cypher_statement(cy)[0]
    if node_id is None:
        non_created_entities.append(inst)

print(len(non_created_entities))


