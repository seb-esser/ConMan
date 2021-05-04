
class Neo4jFactory:

	def __init__(self):
		pass

	# constructs a multi statement cypher command
	@classmethod
	def BuildMultiStatement(self, cypherCMDs):
		return ' '.join(cypherCMDs)


