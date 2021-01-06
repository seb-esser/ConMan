
""

# import numpy as np

from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

from neo4jGraphDiff.RootedNodeDiff import RootedNodeDiff
from neo4jGraphDiff.DirectedSubgraphDiff import DirectedSubgraphDiff


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

label_init = "ts20210106T101528"
label_updated = "ts20210106T101608"

cypher = []

# 1: Check base structure of rooted nodes
rootedNodeDiff = RootedNodeDiff()
rootedNodeDiff.compareRootedNodes(connector, label_init, label_updated)


# 2: Check sub-graphs for each rooted node
subgraphDiff = DirectedSubgraphDiff(label_init, label_updated)

# DEBUG only, implement a for loop over all rooted nodes to query their nodeIDs
#siteId_initial = connector.run_cypher_statement('MATCH (n:IfcSite:{}) RETURN ID(n)'.format(label_init), 'ID(n)')
#siteId_updated = connector.run_cypher_statement('MATCH (n:IfcSite:{}) RETURN ID(n)'.format(label_updated), 'ID(n)')
proxies_init = connector.run_cypher_statement('MATCH (n:IfcBuildingElementProxy:{}) RETURN ID(n)'.format(label_init), 'ID(n)')
proxies_updated = connector.run_cypher_statement('MATCH (n:IfcBuildingElementProxy:{}) RETURN ID(n)'.format(label_updated), 'ID(n)')


for id in zip(proxies_init, proxies_updated): 
	similar = subgraphDiff.compareChildren(connector, id[0], id[0], True, 0)
	print('Object with rootNodeId {} is similar: {}'.format(id, similar))

# 3: 




