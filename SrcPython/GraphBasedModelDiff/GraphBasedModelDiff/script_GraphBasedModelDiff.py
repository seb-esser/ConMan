
""

# import numpy as np

from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

from neo4jGraphDiff.RootedNodeDiff import RootedNodeDiff


# defs

def RemoveNodeConnectionsCreatedByHash():
	match = 'Match(n)-[r:IS_EQUAL_TO]->(p)'
	delete = 'delete r'




def GetAdjacencyMatrixByNodeId(i, j):	
	#match1 = 'MATCH (n) WHERE ID(n) = {}'.format(i)
	#match2 = 'MATCH (m) WHERE ID(m) = {}'.format(j)		
	#case = 'CASE size((n)--(m))'
	#ifState = 'WHEN 0 THEN 0'
	#elseState = 'ELSE 1'
	#endif = 'END AS adjacent'
	#ret = 'RETURN adjacent'
	match1 = 'MATCH (n) WHERE ID(n) = {}'.format(i)
	match2 = 'MATCH (m) WHERE ID(m) = {}'.format(j)
	ret = 'RETURN ID(n), ID(m), EXISTS ((n)--(m)) as is_connected'

	return [match1, match2, ret]

def GetSubGraphOfNode(): 
	match = 'MATCH path  = (n:IfcAlignment)-[*0..100]->(p)' 
	ret = 'RETURN p'

	return [match, ret]

# -- ... --

connector = Neo4jConnector(False, False)
connector.connect_driver()

label_init = "ts20200202T105551"
label_updated = "ts20200204T105551"

cypher = []

# 1: Check base structure of rooted nodes
rootedNodeDiff = RootedNodeDiff()
rootedNodeDiff.compareRootedNodes(connector, label_init, label_updated)


# 2: Check sub-graphs for each rooted node


# 3: 




