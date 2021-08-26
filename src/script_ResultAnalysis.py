import jsonpickle

from neo4jGraphDiff.Result import Result

with open('result_solibriExample.json') as f:
    content = f.read()

result: Result = jsonpickle.decode(content)

# collect all primary elements that have been modified

guids = []

for pm in result.property_updates:
    entity = pm.pattern.get_entry_node().attrs['EntityType']
    guid = pm.pattern.get_entry_node().attrs['GlobalId']
    if guid not in guids:
        guids.append(guid)
        print("GlobalID: {} \t EntityType: {} \t\t {}".format(guid, entity, pm.attrName))


print(len(guids))
