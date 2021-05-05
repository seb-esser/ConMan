""

import asyncio
# import numpy as np
import time

import PatchManager.PatchGenerator
from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.SecondaryNodeDiff import DfsIsomorphismCalculator
from neo4jGraphDiff.Caption.ResultGenerator import ResultGenerator
from neo4jGraphDiff.PrimaryNodeDiff import RootedNodeDiff
from neo4j_middleware.neo4jConnector import Neo4jConnector

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
label_init = "ts20210119T085408" # different rep
label_updated = "ts20210119T085409"	# different rep, modified height

## cuboid sample with cuboid vs cylinder
#label_init = "ts20210119T085410"	# cuboid
#label_updated = "ts20210119T085411"	# cylinder

## cuboid sample with extrudedArea vs BRep
#label_init = "ts20210119T085412"	# extrudedArea
#label_updated = "ts20210119T085413"	# BRep

## wall column sample
#label_init = "ts20200713T083450"
#label_updated = "ts20200713T083447"

#### Residential
#label_init = "ts20210219T121203"
#label_updated = "ts20210219T121608"

## 4x3 Bridges
#label_init = "ts20210118T211240"
#label_updated = "ts20210227T133609"

async def main():
	# set config
	config = Configuration.rel_type_config()
	#config = Configuration.on_guid_config()
	print(config)
	print(config.DiffSettings)

	# init report 
	report = ResultGenerator(ts_init=label_init, ts_updated=label_updated, usedConfig=config)

	cypher = []

	# 1: Check base structure of rooted nodes

	print(' ROOT DIFF \n')

	rootedNodeDiff = RootedNodeDiff(connector, config)

	attrIgnore = config.DiffSettings.diffIgnoreAttrs
	[nodeIDs_unchanged, nodeIDs_added, nodeIDs_deleted] = rootedNodeDiff.diffRootedNodes(label_init, label_updated)

	# save results to report
	report.capture_result_primary([nodeIDs_unchanged, nodeIDs_added, nodeIDs_deleted])

	print('\nCOMPONENT DIFF \n')

	# 2: Check sub-graphs for each rooted node
	DiffEngine = DfsIsomorphismCalculator(connector, label_init, label_updated, config)

	all_tasks = []

	for pair in nodeIDs_unchanged:
		node_init = pair[0]
		node_updated = pair[1]
		print('[TASK] Compare objects with root nodeIDs {}'.format(pair))
	
		# run component diff
		task = asyncio.create_task(DiffEngine.diff_subgraphs_async(node_init, node_updated))
		all_tasks.append(task)
	
	tic = time.process_time()
	result = await asyncio.gather(*all_tasks)
	for res in result:
		report.capture_result_secondary(res)
	toc = time.process_time()
	elapsed = toc - tic
	print('\nOverall time elapsed: {}\n'.format(elapsed))
	# show result on console
	report.print_report()
	# report.print_time_plot()

	# create a patch out of the captured diff result
	generator = PatchManager.PatchGenerator.PatchGenerator()
	generator.create_patch_from_graph_diff(report)

asyncio.run(main())