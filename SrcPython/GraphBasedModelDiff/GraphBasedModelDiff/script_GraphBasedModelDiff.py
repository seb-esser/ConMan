
""

# import numpy as np

from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

from neo4jGraphDiff.RootedNodeDiff import RootedNodeDiff

from neo4jGraphDiff.CompareDiff import CompareDiff
from neo4jGraphDiff.HashDiff import HashDiff


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

label_init = "ts20210106T110329"
label_updated = "ts20210106T110250"

cypher = []

# 1: Check base structure of rooted nodes
rootedNodeDiff = RootedNodeDiff()
rootedNodeDiff.compareRootedNodes(connector, label_init, label_updated)


# 2: Check sub-graphs for each rooted node
diffIgnoreFile = './neo4jGraphDiff/diffIgnore.json'
Diff_onHash = HashDiff(connector, label_init, label_updated, diffIgnorePath = diffIgnoreFile)
Diff_onCompare = CompareDiff(connector, label_init, label_updated, diffIgnorePath = diffIgnoreFile)

# DEBUG only, implement a for loop over all rooted nodes to query their nodeIDs
#siteId_initial = connector.run_cypher_statement('MATCH (n:IfcSite:{}) RETURN ID(n)'.format(label_init), 'ID(n)')
#siteId_updated = connector.run_cypher_statement('MATCH (n:IfcSite:{}) RETURN ID(n)'.format(label_updated), 'ID(n)')

id_init = 477
id_update = 502

print('comparing subgraphs of root node {} with {}'.format(id_init, id_update))

# compares the subgraphs of two nodes that should contain the same data
similarHash = Diff_onHash.diffSubgraphs(id_init, id_update)
print('[RESULT HASH-comp] Object (=Subgraph) with rootNodeId {} is similar to {}: {}'.format(id_init, id_update, similarHash))

similarDiff = Diff_onCompare.diffSubgraphs(id_init, id_update)
print('[RESULT AttrDiff-comp] Object (=Subgraph) with rootNodeId {} is similar to {}: {}'.format(id_init, id_update, similarDiff))

# 3: 




