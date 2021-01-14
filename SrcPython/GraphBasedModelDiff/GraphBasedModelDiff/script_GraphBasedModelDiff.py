
""

# import numpy as np
import time

from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

from neo4jGraphDiff.RootedNodeDiff import RootedNodeDiff

from neo4jGraphDiff.CompareDiff import CompareDiff
from neo4jGraphDiff.HashDiff import HashDiff



# -- ... --

connector = Neo4jConnector(False, False)
connector.connect_driver()

## sleeper sample
#label_init = "ts20200202T105551"
#label_updated = "ts20200204T105551"


# cuboid sample
label_init = "ts20210106T110329"
label_updated = "ts20210106T110250"


## wall column sample
#label_init = "ts20200713T083450"
#label_updated = "ts20200713T083447"

cypher = []

# 1: Check base structure of rooted nodes

print('----------------- [1] ------------------------\n')

rootedNodeDiff = RootedNodeDiff(connector, toConsole=True)

attrIgnore = ["p21_id", "GlobalId"]
[nodeIDs_unchanged, nodeIDs_added, nodeIDs_deleted] = rootedNodeDiff.diffRootedNodes(label_init, label_updated, attrIgnore)


print('\n----------------- [2] ------------------------\n')
# 2: Check sub-graphs for each rooted node
diffIgnoreFile = './neo4jGraphDiff/diffIgnore.json'
Diff_onHash = HashDiff(connector, label_init, label_updated, diffIgnorePath = diffIgnoreFile, LogtoConsole=True, considerRelType=True)
Diff_onCompare = CompareDiff(connector, label_init, label_updated, diffIgnorePath = diffIgnoreFile, LogtoConsole=False)

times_hash = []
for pair in nodeIDs_unchanged: 
	nodeId_init = pair[0]
	nodeId_updated = pair[1]
	print('[TASK HASH-comp] Compare objects with root nodeIDs {}\n'.format(pair))
	t_hash = time.process_time()
	similarHash = Diff_onHash.diffSubgraphs(nodeId_init, nodeId_updated)
	print('[RESULT HASH-comp] Object (=Subgraph) with rootNodeId {} is similar to {}: {}'.format(nodeId_init, nodeId_updated, similarHash))
	elapsed_time_hash = time.process_time() - t_hash
	times_hash.append(elapsed_time_hash)

times_diff = []
for pair in nodeIDs_unchanged: 
	nodeId_init = pair[0]
	nodeId_updated = pair[1]

	t_diff = time.process_time()
	similarHash = Diff_onCompare.diffSubgraphs(nodeId_init, nodeId_updated)
	print('[RESULT DIFF-comp] Object (=Subgraph) with rootNodeId {} is similar to {}: {}'.format(nodeId_init, nodeId_updated, similarHash))
	elapsed_time_diff = time.process_time() - t_diff
	times_diff.append(elapsed_time_diff)

print('elapsed time for HASH based comparison: {}'.format(sum(times_hash)))
print(times_hash)
print('elapsed time for DIFF based comparison: {}'.format(sum(times_diff)))
print(times_diff)

## DEBUG only, implement a for loop over all rooted nodes to query their nodeIDs
#siteId_initial = connector.run_cypher_statement('MATCH (n:IfcSite:{}) RETURN ID(n)'.format(label_init), 'ID(n)')
#siteId_updated = connector.run_cypher_statement('MATCH (n:IfcSite:{}) RETURN ID(n)'.format(label_updated), 'ID(n)')

#id_init = 477
#id_update = 502

#print('comparing subgraphs of root node {} with {}'.format(id_init, id_update))

## compares the subgraphs of two nodes that should contain the same data
#similarHash = Diff_onHash.diffSubgraphs(id_init, id_update)
#print('[RESULT HASH-comp] Object (=Subgraph) with rootNodeId {} is similar to {}: {}'.format(id_init, id_update, similarHash))

#similarDiff = Diff_onCompare.diffSubgraphs(id_init, id_update)
#print('[RESULT AttrDiff-comp] Object (=Subgraph) with rootNodeId {} is similar to {}: {}'.format(id_init, id_update, similarDiff))

# 3: 




