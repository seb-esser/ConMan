


""" This class provides common tools to construct complex cypher request. """
class neo4jQueryUtilities:

	def __init__(self):
		pass

	# constructs a multi statement cypher command
	@classmethod
	def BuildMultiStatement(self, cypherCMDs):
		return ' '.join(cypherCMDs)

	@classmethod
	def removeAttrsFromDict(self, dictionary, exlude):




