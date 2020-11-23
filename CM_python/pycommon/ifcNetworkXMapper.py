
from .ifcMapper import IfcMapper
import networkx as nx
import ifcopenshell 

class IfcNetworkXMapper(IfcMapper): 

	def __init__(self):
		self.G = nx.DiGraph()
		self.ifc_model = None
		super().__init__()

	def loadIfcModel(self, path):
		if path == None:
			print('invalid path to model')
			exit()

		self.ifc_model = ifcopenshell.open(path)
		return self.ifc_model
		 
	




