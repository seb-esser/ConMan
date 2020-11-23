
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
		 
	def getBasicMetaDataFromModel(self):
		ifc_objDefs = self.ifc_model.by_type('IfcObjectDefinition')
		ifc_Rels = self.ifc_model.by_type('IfcRelationship')
		ifc_properties = self.ifc_model.by_type('IfcPropertyDefinition') 

		print(' Amt IfcObjectDefinition: \t {}'.format(len(ifc_objDefs)))
		print(' Amt IfcRelationship: \t {}'.format(len(ifc_Rels)))
		print(' Amt IfcPropertyDefinition: \t {}\n'.format(len(ifc_properties)))

		




