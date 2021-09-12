""

# import numpy as np

from neo4jGraphDiff.GraphDiff import GraphDiff
from neo4j_middleware.neo4jConnector import Neo4jConnector

# -- ... --
connector = Neo4jConnector()
connector.connect_driver()

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

label_init, label_updated = testcases['new_cuboid']

# async def main():
def main():

    diff = GraphDiff(label_init, label_updated)
    patch = diff.run_diff(connector=connector)
    patch.print_report()

# asyncio.run(main())
main()
