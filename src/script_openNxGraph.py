
import jsonpickle

timestamp = "ts20221002T111302"

with open('NetworkX-Graph_{}.json'.format(timestamp)) as f:
    content = f.read()

nx_graph = jsonpickle.decode(content)
print(nx_graph)



