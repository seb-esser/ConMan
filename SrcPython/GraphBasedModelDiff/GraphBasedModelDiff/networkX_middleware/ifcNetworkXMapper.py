
from .ifcMapper import IfcMapper
import networkx as nx
import matplotlib.pyplot as plt
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

		
	def mapEntity(self):
		ifc_objDefs = self.ifc_model.by_type('IfcObjectDefinition')

		for entity in ifc_objDefs:
			
			name = entity.Name
			attrs = entity.get_info()
			globalId = entity.GlobalId
			ent_type = attrs['type']
			ent_id = attrs['id']
			
			# remove type from dict
			# exlude = ['type'] #, 'ownerHistory']
			# attrs_reduced = {key: val for key,val in attrs.items() if key not in exlude}

			print('{:<15} - GUID: {:<18} - Name: {}'.format(ent_type, globalId, name))
			for key, val in attrs.items():
				print('\t{:<15} : {}'.format(key, val))
			print('\n')

			self.G.add_nodes_from(
				[
					(ent_id, attrs)
				])


	def mapObjRelationships(self):
		ifc_Rels = self.ifc_model.by_type('IfcRelationship')

		for rel in ifc_Rels:			
			name = rel.Name
			attrs = rel.get_info()
			globalId = rel.GlobalId
			ent_type = attrs['type']
			ent_id = attrs['id']

			# needs refinements
			relObj = rel.RelatedObjects[0].get_info()['id']

			print('{:<15} - GUID: {:<18} - Name: {}'.format(ent_type, globalId, name))
			for key, val in attrs.items():
				print('\t{:<15} : {}'.format(key, val))
			print('\n')

	def printGraph(self):

		print(self.G.adj)

		plt.plot()
		nx.draw(self.G, with_labels=True, node_color = 'r', edge_color = 'b') # , font_weight='bold')
		plt.show()






