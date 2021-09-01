import jsonpickle

from neo4jGraphDiff.Result import Result

with open('result_solibriExample.json') as f:
    content = f.read()

print("[INFO] loading result json....")
result: Result = jsonpickle.decode(content)
print("[INFO] loading result json: DONE.")
# collect all primary elements that have been modified

guids = []
print("""

-- DIFF REPORT -- 

""")

sorted_pMods = result.sort_pMods_by_guid()

for pm in result.property_updates:
    entity = pm.pattern.get_entry_node().attrs['EntityType']
    guid = pm.pattern.get_entry_node().attrs['GlobalId']
    # if guid not in guids:
    #     guids.append(guid)
    print("{:>12}\t{:<20}\t{:<25}\t{:<100}\t{:<100}".format(guid, entity, pm.attrName, pm.valueOld, pm.valueNew))


print(len(guids))
