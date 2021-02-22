""

# import numpy as np
import time

from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

from neo4jGraphDiff.RootedNodeDiff import RootedNodeDiff

from neo4jGraphDiff.DepthFirstSearchComparison import DepthFirstSearchComparison

from neo4jGraphDiff.Configurator import Configurator
from neo4jGraphDiff.Reporter import Report

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
#label_init = "ts20210119T085410"	# cuboid
#label_updated = "ts20210119T085411"	# cylinder

## cuboid sample with extrudedArea vs BRep
#label_init = "ts20210119T085412"	# extrudedArea
#label_updated = "ts20210119T085413"	# BRep

## wall column sample
label_init = "ts20200713T083450"
label_updated = "ts20200713T083447"

### Residential
#label_init = "ts20210219T121203"
#label_updated = "ts20210219T121608"

# set config
#config = Configurator.relTypeConfig()
config = Configurator.onGuidConfig()
print(config)
print(config.DiffSettings)

# init report 
report = Report(None, config)

cypher = []

# 1: Check base structure of rooted nodes

print(' ROOT DIFF \n')

rootedNodeDiff = RootedNodeDiff(connector, config)

attrIgnore = config.DiffSettings.diffIgnoreAttrs
[nodeIDs_unchanged, nodeIDs_added, nodeIDs_deleted] = rootedNodeDiff.diffRootedNodes(label_init, label_updated)

# save results to report
report.CaptureResult_RootedDiff([nodeIDs_unchanged, nodeIDs_added, nodeIDs_deleted])

print('\nCOMPONENT DIFF \n')

# 2: Check sub-graphs for each rooted node
DiffEngine = DepthFirstSearchComparison(connector, label_init, label_updated, config)


for pair in nodeIDs_unchanged:
	node_init = pair[0]
	node_updated = pair[1]
	print('[TASK] Compare objects with root nodeIDs {}'.format(pair))
	
	# measure time
	t_diff = time.process_time()

	# run component diff
	DiffResult = DiffEngine.diffSubgraphs(node_init, node_updated)

	# stop time
	elapsed_time_diff = time.process_time() - t_diff
	
	# add computational time to diff result
	DiffResult.setComputeTime(elapsed_time_diff)

	# save diffResult to report
	report.CaptureResult_ComponentDiff(DiffResult)
	print('[TASK] DONE')
		

# show result on console
report.printResultToConsole()
report.printTimeFigures()
