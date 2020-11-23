
from .ifcMapper import IfcMapper
import networkx as nx

class IfcNetworkXMapper(IfcMapper): 

	def __init__(self):
		self.G = nx.DiGraph()
		super().__init__()




