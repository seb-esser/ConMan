

class IfcObjRelCacher:
	
	def __init__(self, ty, guid, guidOwnerHist):

		self.RelType = ty
		self.globalId = guid
		self.ownerHistory = guidOwnerHist
		self.outgoing_Rels = []
		self.incoming_Rels = []

	def AddOutgoingRel(self, outgoing):
		self.outgoing_Rels.append(outgoing)

	def AddIncomingRel(self, incoming):
		self.incoming_Rels.append(incoming)


class Rel:
	
	def __init__(self, ty, target):
		self.type = ty
		self.target_guid = target







