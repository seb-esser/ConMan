

from .neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

class neo4jGraphFactory:

	def __init__(self):
		pass


	@classmethod
	def CreateRelationship(cls, sourceNodeId, targetNodeId, qualifier, rel_type, ref):
		match_source = 'MATCH(s) where ID(s) = {}'.format(sourceNodeId)
		match_target = 'MATCH(t) where ID(t) = "{}"'.format(targetNodeId)
		merge = 'MERGE (s)-[r.{}]->(t)'.format(rel_type)
		#set_qualifier = 'SET r.Qualifier = {}'.format(qualifier)
		return neo4jUtils.BuildMultiStatement([match_source, match_target, merge, set_qualifier])

	@classmethod
	def CreateRootedNode(cls, entityId, entityType, timestamp):
		create = 'CREATE(n:{}:rootedNode:{})'.format(entityType, timestamp)
		setGuid = 'SET n.GlobalId = "{}"'.format(entityId)
		setEntityType = 'SET n.entityType = "{}"'.format(entityType)
		returnID = 'RETURN ID(n)'
		return neo4jUtils.BuildMultiStatement([create, setGuid, setEntityType, returnID])

	@classmethod
	def AddAttributesToNode(self, nodeId, attributes, timestamp):
		match = 'MATCH(n:{}) WHERE ID(n) = {}'.format(timestamp, nodeId)
		attrs = []
		for attr, val in attributes.items(): 
			if isinstance(val, str):
				add_param = 'SET n.{} = "{}"'.format(attr, val)
				attrs.append(add_param)
			elif isinstance(val, (int, float, complex)):
				add_param = 'SET n.{} = {}'.format(attr, val)
				attrs.append(add_param)
			else: 
				# ToDo: throw exeption
				print('ERROR when adding attributes to existing node. check your inputs. ')

		returnID = 'RETURN n'

		return neo4jUtils.BuildMultiStatement([match] + attrs + [returnID])

	@classmethod
	def CreateAttributeNode(self, ParentId, NodeLabel, RelationshipLabel, timestamp):
		match = 'MATCH (p) WHERE ID(p) = {}'.format(ParentId)
		create = 'CREATE (n: {}:attrNode:{})'.format(NodeLabel, timestamp)             
		merge = 'MERGE (p)-[:{}]->(n)'.format(RelationshipLabel)
		returnID = 'RETURN ID(n)'

		return neo4jUtils.BuildMultiStatement([match, create, merge, returnID])

	@classmethod
	def MergeRootedNodeWithOwnerHistory(self, ownerHistoryGuid, myNodeId, timeStamp):
		match = 'MATCH (p:{}) WHERE p.globalId = "{}"'.format(timeStamp, ownerHistoryGuid)
		matchOwn = 'MATCH (me) WHERE ID(me) = {}'.format(myNodeId)
		merge = 'MERGE (me)-[:{}]->(p)'.format('IfcOwnerHistory')
		returnID = 'RETURN ID(me)'
		return neo4jUtils.BuildMultiStatement([match, matchOwn, merge, returnID])

	@classmethod 
	def CreateObjectifiedRelNode(self, relGuid, relType, timestamp):
		create = 'CREATE(n:{}:objRelNode:{})'.format(relType, timestamp)
		setGuid = 'SET n.globalId = "{}"'.format(relGuid)
		setEntityType = 'SET n.entityType = "{}"'.format(relType)
		returnID = 'RETURN ID(n)'
		return neo4jUtils.BuildMultiStatement([create, setGuid, setEntityType, returnID])

	@classmethod 
	def MergeObjRelWithRootedNode(self, objRelGuid, targetNodeGuid, TypeFromRelToNode, TypeFromNodeToRel, timestamp):
		matchObjRel = 'MATCH (objrel:{}) WHERE objrel.globalId = "{}"'.format(timestamp, objRelGuid)
		matchRootedObj = 'MATCH (rooted:{}) WHERE rooted.globalId = "{}"'.format(timestamp, targetNodeGuid)
		merge1 = 'MERGE (objrel)-[:{}]->(rooted)'.format(TypeFromRelToNode)
		merge2 = 'MERGE (objrel)<-[:{}]-(rooted)'.format(TypeFromNodeToRel)
		returnID = 'RETURN ID(rooted)'
		return neo4jUtils.BuildMultiStatement([matchObjRel, matchRootedObj, merge1, merge2, returnID])

	@classmethod
	def DeleteNode(self, nodeId):
		match = 'MATCH (n) WHERE ID(n) = {}'.format(nodeId)
		detach = 'DETACH'
		delete = 'DELETE n'
		return neo4jUtils.BuildMultiStatement([match, detach, delete])

