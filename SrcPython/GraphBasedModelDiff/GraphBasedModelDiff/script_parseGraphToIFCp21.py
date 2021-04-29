

from ifc_middleware.IfcGenerator import IfcGenerator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.NodeItem import NodeItem

connector = Neo4jConnector(False, False)
connector.connect_driver()

generator = IfcGenerator()
query_factory = Neo4jQueryFactory()

ts = "ts20210119T085408"

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



    # build association
    cy = query_factory.get_child_nodes(ts, n.id)
    raw_res = connector.run_cypher_statement(cy)

    # cast cypher response in a list of node items
    childs = NodeItem.fromNeo4jResponseWithRel(raw_res)

    for c in childs:
        # query all node properties of n
        cy = query_factory.get_node_properties_by_id(c.id)
        raw_res = connector.run_cypher_statement(cy, "properties(n)")
        # assign properties to node object
        c.setNodeAttributes(raw_res)

        c.tidy_attrs()

        # build IFC entity
        generator.build_entity(c.id, c.entityType, c.attrs)

        # build association
        generator.build_association(n.id, c.id, c.relType)

generator.save_model(ts)

connector.disconnect_driver()

