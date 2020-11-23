
# --- imports ---
import networkx as nx
import matplotlib.pyplot as plt

# --- script ---

G_initial = nx.Graph()
G_updated = nx.Graph()

G_initial.add_nodes_from(
	[
	(1, {"name": "project"}),
	(2, {"name": "site"})
	]
						 )

G_initial.add_edge(1, 2)

print(list(G_initial.nodes))
print(list(G_initial.edges))

plt.subplot(121)
nx.draw(G_initial, with_labels=True, font_weight='bold')
plt.show()
