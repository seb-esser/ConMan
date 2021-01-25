""

# import numpy as np
import time

from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

from neo4jGraphDiff.RootedNodeDiff import RootedNodeDiff

from neo4jGraphDiff.CompareDiff import CompareDiff
from neo4jGraphDiff.HashDiff import HashDiff

from neo4jGraphDiff.Configurator import Configurator

# -- ... --

connector = Neo4jConnector(False, False)
connector.connect_driver()

## sleeper sample
# label_init = "ts20200202T105551"
# label_updated = "ts20200204T105551"


## cuboid sample with different subgraph structures
#label_init = "ts20210119T085406"	# same rep
#label_updated = "ts20210119T085407" # different rep

## cuboid sample with height elevation 
#label_init = "ts20210119T085408" # different rep
#label_updated = "ts20210119T085409"	# different rep, modified height

## cuboid sample with cuboid vs cylinder
label_init = "ts20210119T085410"	# cuboid
label_updated = "ts20210119T085411"	# cylinder

## cuboid sample with extrudedArea vs BRep
#label_init = "ts20210119T085412"	# extrudedArea
#label_updated = "ts20210119T085413"	# BRep

## wall column sample
#label_init = "ts20200713T083450"
#label_updated = "ts20200713T083447"


config = Configurator.basicConfig()

cypher = []

# 1: Check base structure of rooted nodes

print('----------------- [1] ------------------------\n')

rootedNodeDiff = RootedNodeDiff(connector, toConsole=True)

attrIgnore = ["p21_id", "GlobalId"]
[nodeIDs_unchanged, nodeIDs_added, nodeIDs_deleted] = rootedNodeDiff.diffRootedNodes(label_init, label_updated,
																					 attrIgnore)

print('\n----------------- [2] ------------------------\n')
# 2: Check sub-graphs for each rooted node
diffIgnoreFile = './neo4jGraphDiff/diffIgnore.json'
Diff_onHash = HashDiff(connector, label_init, label_updated, diffIgnorePath=diffIgnoreFile, LogtoConsole=False,
					   considerRelType=True)
Diff_onCompare = CompareDiff(connector, label_init, label_updated, diffIgnorePath=diffIgnoreFile, LogtoConsole=False,
							 considerRelType=True)

times_hash = []
times_diff = []

for pair in nodeIDs_unchanged:
	node_init = pair[0]
	node_updated = pair[1]
	print('[TASK] Compare objects with root nodeIDs {}'.format(pair))

	t_hash = time.process_time()
	HashResult = Diff_onHash.diffSubgraphs(node_init, node_updated)
	elapsed_time_hash = time.process_time() - t_hash
	times_hash.append(elapsed_time_hash)

	t_diff = time.process_time()
	DiffResult = Diff_onCompare.diffSubgraphs(node_init, node_updated)

	elapsed_time_diff = time.process_time() - t_diff
	times_diff.append(elapsed_time_diff)

	print('[RESULT HASH-comp] Object with rootNodeId {} is similar to {}: {}'.format(node_init.id, node_updated.id,
																								 HashResult.isSimilar))
	#if not HashResult.isSimilar:
	#	print('\t Detected changes in HASH comparison:')
	#	for res in HashResult.propertyModifications:
	#		print(res)

	#	for res in HashResult.StructureModifications:
	#		print(res)

	print('[RESULT DIFF-comp] Object with rootNodeId {} is similar to {}: {}'.format(node_init.id, node_updated.id,
																								 DiffResult.isSimilar))

	if not DiffResult.isSimilar:
		print('\t Detected changes in DIFF comparison:')
		for res in DiffResult.propertyModifications:
			print(res)

		for res in DiffResult.StructureModifications:
			print(res)
	print()

print('Overview computational times: ')
print('elapsed time for HASH based comparison: {}'.format(sum(times_hash)))
print(times_hash)
print('elapsed time for DIFF based comparison: {}'.format(sum(times_diff)))
print(times_diff)

## DEBUG only, implement a for loop over all rooted nodes to query their nodeIDs
# siteId_initial = connector.run_cypher_statement('MATCH (n:IfcSite:{}) RETURN ID(n)'.format(label_init), 'ID(n)')
# siteId_updated = connector.run_cypher_statement('MATCH (n:IfcSite:{}) RETURN ID(n)'.format(label_updated), 'ID(n)')

# id_init = 477
# id_update = 502

# print('comparing subgraphs of root node {} with {}'.format(id_init, id_update))

## compares the subgraphs of two nodes that should contain the same data
# similarHash = Diff_onHash.diffSubgraphs(id_init, id_update)
# print('[RESULT HASH-comp] Object (=Subgraph) with rootNodeId {} is similar to {}: {}'.format(id_init, id_update, similarHash))

# similarDiff = Diff_onCompare.diffSubgraphs(id_init, id_update)
# print('[RESULT AttrDiff-comp] Object (=Subgraph) with rootNodeId {} is similar to {}: {}'.format(id_init, id_update, similarDiff))

# 3:
