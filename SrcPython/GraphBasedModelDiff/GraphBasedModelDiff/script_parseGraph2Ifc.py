

from IfcGraphInterface.Graph2IfcTranslator import IfcGenerator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector

# this function can either be recursive or non-recursive, depending on 'rec'
def build_childs(n, rec):
    # build association
    cy = query_factory.get_child_nodes(ts, n.id)
    raw_res = connector.run_cypher_statement(cy)

    # cast cypher response in a list of node items
    childs = NodeItem.fromNeo4jResponseWithRel(raw_res)
    if len(childs) == 0:
        return

    for c in childs:
        # query all node properties of n
        cy = query_factory.get_node_properties_by_id(c.id)
        raw_res = connector.run_cypher_statement(cy, "properties(n)")
        # assign properties to node object
        c.setNodeAttributes(raw_res)

        c.tidy_attrs()

        # check if IFC counterpart to current node was already initialized
        spf_id = generator.lookup_ifc_counterpart_exists(c.id)
        if spf_id == -1:
            # build IFC entity
            generator.build_entity(c.id, c.entityType, c.attrs)

        # build association
        generator.build_association(n.id, c.id, c.relType)

        if rec:
            build_childs(c, True)


connector = Neo4jConnector()
connector.connect_driver()

generator = IfcGenerator()
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

    build_childs(n, True)

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
    build_childs(cnode, False)

    

generator.save_model('test2')

connector.disconnect_driver()

