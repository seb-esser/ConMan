import jsonpickle

from neo4jGraphDiff.GraphDelta import GraphDelta
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


def main():
    ts_init = "ts"
    ts_updated = "ts"

    connector = Neo4jConnector()
    connector.connect_driver()

    # load graph delta
    with open('GraphDelta_initts20210623T091748-updtts20210623T091749.json') as f:
        content = f.read()

    print("[INFO] loading delta json....")
    result: GraphDelta = jsonpickle.decode(content)
    print("[INFO] loading delta json: DONE.")

    # get nodes actually removed or inserted
    cy_removedNodes = "match pa = (n:ts20210623T091749)-[:rel]-(m:ts20210623T091749) WHERE  NOT (n)-[:SIMILAR_TO]-() AND NOT (m)-[:SIMILAR_TO]-() return pa,  NODES(pa), RELATIONSHIPS(pa)"
    raws = connector.run_cypher_statement(cy_removedNodes)
    pt = GraphPattern.from_neo4j_response(raws)

    nodes_removed = pt.get_unified_node_set()

    print('embedding:')
    for i in nodes_removed:
        cy_equ_neighbor = "match p = (n)-[r:rel]->(e)-[:SIMILAR_TO]-() WHERE ID(n) = {} return e".format(i.id)
        raw_neighbor = connector.run_cypher_statement(cy_equ_neighbor)
        if raw_neighbor != []:

            ref_node = NodeItem.from_neo4j_response(raw_neighbor[0])[0]
            # get "first visited from"
            parent_node = result.node_matching_table.get_parent_primaryNode(ref_node)
            print(parent_node)

            # calculate shortest path
            # "MATCH {}, {} ".format(parent_node.to_cypher(skip_labels=True), )

    connector.disconnect_driver()


if __name__ == "__main__":
    main()
