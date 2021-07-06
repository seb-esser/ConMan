

from IfcGraphInterface.Graph2IfcTranslator import Graph2IfcTranslator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

generator = Graph2IfcTranslator()
query_factory = Neo4jQueryFactory()

ts = "ts20200928T074754"

# get all primary nodes
cy = query_factory.get_primary_nodes(ts)
raw_res = connector.run_cypher_statement(cy)

# cast cypher response in a list of node items
nodes = NodeItem.fromNeo4jResponseWouRel(raw_res)

for n in nodes:
    # query all node properties of n
    cy = query_factory.get_node_properties_by_id(n.id)
    raw_res = connector.run_cypher_statement(cy, "properties(n)")
    # assign properties to node object
    n.setNodeAttributes(raw_res)

    n.tidy_attrs()

    # build IFC entity
    generator.build_entity(n.id, n.entityType, n.attrs)

    generator.build_childs(n, True, connector, ts)

# get all connection nodes
cn = query_factory.get_connection_nodes(ts)
raw_res = connector.run_cypher_statement(cn)

connection_nodes = NodeItem.fromNeo4jResponseWouRel(raw_res)

for cnode in connection_nodes:
    cy = query_factory.get_node_properties_by_id(cnode.id)
    raw_res = connector.run_cypher_statement(cy, "properties(n)")
    # assign properties to node object
    cnode.setNodeAttributes(raw_res)

    cnode.tidy_attrs()

    # build IFC entity
    generator.build_entity(cnode.id, cnode.entityType, cnode.attrs)

    # build the childe (non-recursive)
    generator.build_childs(n, False, connector, ts)

    

generator.save_model('test2')

connector.disconnect_driver()

