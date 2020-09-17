

class IfcRelCommon:

	relatingElementId = None
	relatedElementIds = None
	relatingType = None
	relatedType= None

	def __init__(self, relElement, relatingElems):

		self.relatingElementId = relElement
		self.relatedElementsIds = relatingElems


	def GetNodeIdByGuid(self, guid): 
		return None





