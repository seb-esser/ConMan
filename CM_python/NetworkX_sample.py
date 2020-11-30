
# --- imports ---
import networkx as nx
from networkx.algorithms import isomorphism
import matplotlib.pyplot as plt

# --- script ---

G_initial = nx.DiGraph()
G_updated = nx.DiGraph()

G_initial.add_nodes_from(
	[
	('project', {"name": "project", "type": "IfcProject"}),
	('relAggrs', {"type": "IfcRelAggregates"}),
	('s', {"name": "site"})
	]
)
G_updated.add_nodes_from(
	[
	('p', {"name": "project_new", "type": "IfcProject"}),
	('relAggrs1', {"type": "IfcRelAggregates"}),
	('s', {"name": "site2"}),
	('relAggrs2', {"type": "IfcRelAggregates"}),
	('b1', {"name": "building1", "type":"IfcBuilding"}), 
	('b2', {"name": "building2", "type":"IfcBuilding"})
	]
)

G_initial.add_edges_from(
	[
		('relAggrs', 'project', 
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
		
		( 'relAggrs2', 'b1',
			{'rel': 'IfcRelAggregates', 
			'id': '789abc789def', 
			'direction': 'aggregating'}),
		( 'relAggrs2', 'b2',
			{'rel': 'IfcRelAggregates', 
			'id': '789abc789def', 
			'direction': 'aggregating'}),
		#( 'b', 'relAggrs2', 
		#	{'rel': 'IfcRelAggregates', 
		#	'id': '789abc789def', 
		#	'direction': 'aggregating'})

	]
)

#print(G_initial.nodes.data)
#print(G_updated.nodes.data)
#print(G_initial.edges.data)
#print(G_updated.edges.data)
#print(G_initial.adj)

#plt.plot()
plt.subplot(1, 2, 1)
nx.draw(G_initial, with_labels=True, node_color = 'r', edge_color = 'b', font_weight='bold')
plt.subplot(1, 2, 2)
nx.draw(G_updated, with_labels=True, node_color = 'y', edge_color = 'g', font_weight='bold')
plt.show()

# -- subgraph isomorphism
print('calculating subgraph isomorphism...')

# a subgraph of G_updated is isomorphic to G_initial
GM1 = isomorphism.DiGraphMatcher(G_initial, G_updated)
print('A subgraph of G_initial is isomorphic to G_updated: {}'.format(GM1.subgraph_is_isomorphic()))
print('A subgraph of G_initial is monomorphic to G_updated: {}'.format(GM1.subgraph_is_monomorphic()))

# a subgraph of G_initial is isomorphic to G_initial
GM2 = isomorphism.DiGraphMatcher(G_updated ,G_initial)
print('A subgraph of G_updated is isomorphic to G_initial: {}'.format(GM2.subgraph_is_isomorphic()))
print('A subgraph of G_updated is monomorphic to G_initial: {}'.format(GM2.subgraph_is_monomorphic()))

# node comparison
print('\n--- Calculating node matching')

nodes_init = G_initial.nodes.items()
nodes_updated = G_updated.nodes.items()

print('Nodes G_initial')
for node in nodes_init:
	print(node)
print('Nodes G_updated')
for node in nodes_updated:
	print(node)

# ToDo: Implement node-comparison with dunder __equl__ method

