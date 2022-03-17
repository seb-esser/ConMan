import jsonpickle

from neo4jGraphDiff.GraphDelta import GraphDelta

with open('GraphDelta_initts20220210T102821-updtts20220210T103359.json') as f:
    content = f.read()

print("[INFO] loading delta json....")
result: GraphDelta = jsonpickle.decode(content)
print("[INFO] loading delta json: DONE.")
# collect all primary elements that have been modified

print("""

-- DIFF REPORT -- 

""")

print("\n__ property changes __\n")

sorted_pMods = result.sort_pMods_by_guid()

for pm in result.property_updates:
    primary_node_type = pm.pattern.get_entry_node().attrs['EntityType']
    guid = pm.pattern.get_entry_node().attrs['GlobalId']
    modified_node = pm.node_init.attrs['EntityType']
    # if guid not in guids:
    #     guids.append(guid)
    print("{:>12}\t{:<20}\t{:<20}\t{:<25}\t{:<100}\t{:<100}".format(guid, primary_node_type, modified_node, pm.attrName, pm.valueOld, pm.valueNew))

print("\n__ structural changes __\n")

for smod in result.structure_updates:
    parent = smod.parent.attrs['EntityType']
    parend_id = smod.parent.id

    child = smod.child.attrs['EntityType']
    child_id = smod.child.id

    ty = smod.modType

    print("{:>12}\t{:<8}\t{:<25}\t{:<25}\t{:<25}".format(parent, parend_id, child, child_id, ty))
