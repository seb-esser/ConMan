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
connector = Neo4jConnector()
connector.connect_driver()

testcases = {"sleeperExample": ("ts20200202T105551", "ts20200204T105551"),
             "cuboid_differentSubgraphs": ("ts20210119T085406", "ts20210119T085407"),
             "cuboid_changedElevation": ("ts20210119T085408", "ts20210119T085409"),
             "cuboid_vs_cylinder": ("ts20210119T085410", "ts20210119T085411"),
             "cuboid_extruded_vs_BRep": ("ts20210119T085412", "ts20210119T085413"),
             "wall_column": ("ts20200713T083450", "ts20200713T083447"),
             "residential": ("ts20210219T121203", "ts20210219T121608"),
             "4x3_bridges": ("ts20210118T211240", "ts20210227T133609"),
             "Storey": ("ts20210521T074802", "ts20210521T074934")
             }

label_init, label_updated = testcases['Storey']


async def main():
    # set config
    config = Configuration.rel_type_config()
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
        # res = DiffEngine.diff_subgraphs(node_init, node_updated)
        # report.capture_result_secondary(res)

        # run component diff async
        task = asyncio.create_task(DiffEngine.diff_subgraphs_async(node_init, node_updated))
        all_tasks.append(task)

    # tic = time.process_time()
    result = await asyncio.gather(*all_tasks)
    for res in result:
        report.capture_result_secondary(res)
    # toc = time.process_time()
    # elapsed = toc - tic
    # print('\nOverall time elapsed: {}\n'.format(elapsed))

    # show result on console
    report.print_report()
    # report.print_time_plot()

    # create a patch out of the captured diff result
    generator = PatchManager.PatchGenerator.PatchGenerator(connector)
    generator.create_patch_from_graph_diff(report)

    js_rep = generator.export_to_json()
    print(js_rep)


asyncio.run(main())
