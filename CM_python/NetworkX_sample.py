
# --- imports ---
import networkx as nx
import matplotlib.pyplot as plt

# --- script ---

G_initial = nx.DiGraph()
G_updated = nx.DiGraph()

G_initial.add_nodes_from(
	[
	('p', {"name": "project"}),
	('s', {"name": "site"})
	]
						 )

G_initial.add_edges_from(
	[
		('p', 's', {'rel': 'IfcRelAggregates',
					'id': 'ad-23.53'}), 
		('s', 'p', {'rel': 'IfcRelAggregates'})
	]
)

print(G_initial.nodes.data)
print(G_initial.edges.data)
print(G_initial.adj)

plt.plot()
nx.draw(G_initial, with_labels=True, node_color = 'r', edge_color = 'b', font_weight='bold')
plt.show()
