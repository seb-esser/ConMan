"""
Script to calculate the pattern size (i.e. number of nodes) to modify a property
2021-09-01 SE
"""
import jsonpickle

from neo4jGraphDiff.GraphDelta import GraphDelta

with open('result_initts20121017T152740-updtts20121017T154702.json') as f:
    content = f.read()
    print("[INFO] loading delta json....")
    result: GraphDelta = jsonpickle.decode(content)
    print("[INFO] DONE. ")


node_matching_table = result.node_matching_table
pMods = result.property_updates

print(len(pMods))
#
# for pm in pMods:
#     modified_node = pm.node_init
#     index = node_matching_table.get_parent_primaryNode(modified_node)
#     print('Path length for modification of {}: {}'.format(pm.attrName, index))

