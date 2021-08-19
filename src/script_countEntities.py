# Solibri example
import ifcopenshell
import matplotlib.pyplot as plt
import numpy as np
import operator


label_init = 'ts20121017T152740'
label_updated = 'ts20121017T154702'

path_init = './00_sampleData/IFC_stepP21/solibri_example/pretty_SolibriBuilding.ifc'
path_updt = './00_sampleData/IFC_stepP21/solibri_example/pretty_SolibriBuilding-modified.ifc'

model = ifcopenshell.open(path_init)

types = set(i.is_a() for i in model)
types_count = {t: len(model.by_type(t)) for t in types}

num_elems = sorted(types_count.items(), key = lambda kv:kv[1], reverse = True)
num_elems = [occurence for occurence in num_elems if occurence[1] > 500]


x_values = [val[0] for val in num_elems]
y_values = [val[1] for val in num_elems]

objects = x_values
y_pos = np.arange(len(objects))
performance = y_values

plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects, rotation=90, size=10)


plt.ylabel('No of num_elems')
plt.title('IFC entity types frequency')

plt.show()


