from GraphBasedModelDiff.neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum
from GraphBasedModelDiff.neo4jGraphDiff.SetCalculator import SetCalculator
from GraphBasedModelDiff.neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from GraphBasedModelDiff.neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

# Solibri example
label_init = 'ts20121017T152740'
label_updated = 'ts20121017T154702'

prim_nodes_init = NodeItem.fromNeo4jResponseWouRel(
    connector.run_cypher_statement(
        Neo4jQueryFactory.get_primary_nodes(label_init)
    ))

prim_nodes_updt = NodeItem.fromNeo4jResponseWouRel(
    connector.run_cypher_statement(
        Neo4jQueryFactory.get_primary_nodes(label_updated)
    ))


calculator = SetCalculator()
[unc, added, deleted] = calculator.calc_intersection(prim_nodes_init, prim_nodes_updt, MatchCriteriaEnum.OnGuid)

print('Deleted PrimaryNodes:')
for n in deleted:
    print(n)
print('\nAdded PrimaryNodes: ')
for n in added:
    print(n)

