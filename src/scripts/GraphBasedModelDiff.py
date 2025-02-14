from neo4jGraphDiff.GraphDiff import GraphDiff
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


def diff(label_init, label_updated):
    connector = Neo4jConnector()
    connector.connect_driver()

    # async def main():
    # get topmost entry nodes
    raw_init = connector.run_cypher_statement(
        """
        MATCH (n:PrimaryNode:{} {{EntityType: "IfcProject"}})
        RETURN ID(n), n.EntityType, PROPERTIES(n), LABELS(n)
        """.format(label_init))

    raw_updated = connector.run_cypher_statement(
        """
        MATCH (n:PrimaryNode:{} {{EntityType: "IfcProject"}})
        RETURN ID(n), n.EntityType, PROPERTIES(n), LABELS(n)
        """.format(label_updated))

    entry_init: NodeItem = NodeItem.from_neo4j_response(raw_init)[0]
    entry_updated: NodeItem = NodeItem.from_neo4j_response(raw_updated)[0]

    diff = GraphDiff(connector, label_init, label_updated)
    delta = diff.diff_graphs(entry_init, entry_updated)

    print(delta)


if __name__ == "__main__":
    testcases = {"sleeperExample": ("ts20200202T105551", "ts20200204T105551"),
                 "cuboid_differentSubgraphs": ("ts20210119T085406", "ts20210119T085407"),
                 "cuboid_changedElevation": ("ts20210119T085408", "ts20210119T085409"),
                 "cuboid_vs_cylinder": ("ts20210119T085410", "ts20210119T085411"),
                 "cuboid_extruded_vs_BRep": ("ts20210119T085412", "ts20210119T085413"),
                 "wall_column": ("ts20200713T083450", "ts20200713T083447"),
                 "residential": ("ts20210219T121203", "ts20210219T121608"),
                 "4x3_bridges": ("ts20210118T211240", "ts20210227T133609"),
                 "Storey": ("ts20210521T074802", "ts20210521T074934"),
                 "new_cuboid": ("ts20210623T091748", "ts20210623T091749")
                 }

    l_init, l_updt = testcases['new_cuboid']
    diff(label_init=l_init, label_updated=l_updt)
