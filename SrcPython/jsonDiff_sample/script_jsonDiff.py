
import json
import jsonpatch # use pip install jsonpatch and refer to unitTests in the Git to understand how the module works


file1 = "JsonSample_init.json"
file2 = "JsonSample_update.json"

with open(file1) as f1:
    data1 = json.load(f1)

with open(file2) as f2:
    data2 = json.load(f2)

# create the patch
res = jsonpatch.make_patch(data1, data2)
print('Patch: ')
for r in res:
    print(r)


# applying the patch
patched = jsonpatch.apply_patch(data1, res)
print('\n')
print(patched)


