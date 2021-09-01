import jsonpickle

from neo4jGraphDiff.Result import Result

with open('result_initts20210623T091748-updtts20210623T091749.json') as f:
    content = f.read()
    print("[INFO] loading result json....")
    result: Result = jsonpickle.decode(content)
    print("[INFO] DONE. ")


node_matching_table = result.node_matching_table
pMods = result.property_updates

for pm in pMods:
    modified_node = pm.node_init
    index = node_matching_table.get_parent_primaryNode(modified_node)

