

class IfcRelCommon:

	relatingElementId
	relatedElementIds
	relatingType 
	relatedType

	def __init__(self, relElement, relatingElems):

		self.relatingElementId = relElement
		self.relatedElementsIds = relatingElems


	def GetNodeIdByGuid(self, guid): 
		return None





