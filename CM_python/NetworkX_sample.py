
# --- imports ---
import networkx as nx
from networkx.algorithms import isomorphism
import matplotlib.pyplot as plt

# --- script ---

G_initial = nx.MultiDiGraph()
G_updated = nx.MultiDiGraph()

G_initial.add_nodes_from(
	[
	('p', {"name": "project", "type": "IfcProject"}),
	('relAggrs', {"type": "IfcRelAggregates"}),
	('s', {"name": "site"})
	]
)
G_updated.add_nodes_from(
	[
	('p', {"name": "project_new"}),
	('relAggrs1', {"type": "IfcRelAggregates"}),
	('s', {"name": "site2"}),
	('relAggrs2', {"type": "IfcRelAggregates"}),
	('b', {"name": "building", "type":"IfcBuilding"})
	]
)

G_initial.add_edges_from(
	[
		('relAggrs', 'p', 
			{'rel': 'IfcRelAggregates', 
			'id': '123abc456def', 
			'direction': 'relatingObject'}), 
		#('p', 'relAggrs1',  
		#	{'rel': 'IfcRelAggregates', 
		#	'id': '123abc456def', 
		#	'direction': 'aggregates'}),

		('relAggrs', 's', 
			{'rel': 'IfcRelAggregates', 
			'id': '123abc456def', 
			'direction': 'relatedObjects'}),
		#('s', 'relAggrs1', 
		#	{'rel': 'IfcRelAggregates', 
		#	'id': '123abc456def', 
		#	'direction': 'aggegating'})
	]
)

G_updated.add_edges_from(
	[
		('relAggrs1', 'p', 
			{'rel': 'IfcRelAggregates', 
			'id': '123abc456def', 
			'direction': 'relatingObject'}), 
		#('p', 'relAggrs1',  
		#	{'rel': 'IfcRelAggregates', 
		#	'id': '123abc456def', 
		#	'direction': 'aggregates'}),
		('relAggrs1', 's', 
			{'rel': 'IfcRelAggregates', 
			'id': '123abc456def', 
			'direction': 'relatedObjects'}),
		#('s', 'relAggrs1', 
		#	{'rel': 'IfcRelAggregates', 
		#	'id': '123abc456def', 
		#	'direction': 'aggegating'}),

		('relAggrs2', 's', 
			{'rel': 'IfcRelAggregates', 
			'id': '789abc789def', 
			'direction': 'relatingObject'}), 
		#( 's', 'relAggrs2',
		#	{'rel': 'IfcRelAggregates', 
		#	'id': '789abc789def', 
		#	'direction': 'aggregates'}),
		
		( 'relAggrs2', 'b',
			{'rel': 'IfcRelAggregates', 
			'id': '789abc789def', 
			'direction': 'aggregating'}),
		#( 'b', 'relAggrs2', 
		#	{'rel': 'IfcRelAggregates', 
		#	'id': '789abc789def', 
		#	'direction': 'aggregating'})

	]
)

print(G_initial.nodes.data)
print(G_updated.nodes.data)
print(G_initial.edges.data)
print(G_updated.edges.data)
#print(G_initial.adj)

plt.plot()
nx.draw(G_initial, with_labels=True, node_color = 'r', edge_color = 'b', font_weight='bold')
nx.draw(G_updated, with_labels=True, node_color = 'y', edge_color = 'g', font_weight='bold')
#plt.show()

# -- subgraph isomorphism
print('calculating subgraph isomorphism...')

GM1 = isomorphism.MultiDiGraphMatcher(G_initial, G_updated)
print('G_initial is isomorphic subgraph of G_updated: {}'.format(GM1.subgraph_is_isomorphic()))

GM2 = isomorphism.MultiDiGraphMatcher(G_updated ,G_initial)
print('G_updated is isomorphic subgraph of G_initial: {}'.format(GM2.subgraph_is_isomorphic()))

# node comparison
print('\nCalculating node matching')

nodes_init = G_initial.nodes.items()
nodes_updated = G_updated.nodes.items()

for node in nodes_init:
	print(node)
for node in nodes_updated:
	print(node)

# ToDo: Implement node-comparison with dunder __equl__ method

