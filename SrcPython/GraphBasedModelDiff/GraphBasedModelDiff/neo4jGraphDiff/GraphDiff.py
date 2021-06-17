import asyncio

from neo4jGraphDiff.Caption.ResultGenerator import ResultGenerator
from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.PrimaryNodeDiff import RootedNodeDiff
from neo4jGraphDiff.SecondaryNodeDiff import DfsIsomorphismCalculator
from neo4j_middleware.neo4jConnector import Neo4jConnector


class GraphDiff:
    def __init__(self, label_init: str, label_updated: str):
        self.config = Configuration.rel_type_config()
        print(self.config)
        print(self.config.DiffSettings)
        self.label_init = label_init
        self.label_updated = label_updated

        self.report = ResultGenerator(ts_init=label_init, ts_updated=label_updated, usedConfig=self.config)

    def run_diff(self, connector: Neo4jConnector):
        cypher = []

        # 1: Check base structure of rooted nodes

        print(' ROOT DIFF \n')

        rootedNodeDiff = RootedNodeDiff(connector, self.config)

        [nodeIDs_unchanged, nodeIDs_added, nodeIDs_deleted] = rootedNodeDiff.diffRootedNodes(self.label_init, self.label_updated)

        # save results to report
        self.report.capture_result_primary([nodeIDs_unchanged, nodeIDs_added, nodeIDs_deleted])

        print('\n COMPONENT DIFF \n')

        # 2: Check sub-graphs for each rooted node
        DiffEngine = DfsIsomorphismCalculator(connector, self.label_init, self.label_updated, self.config)

        self.calc_secondary(DiffEngine, nodeIDs_unchanged)

        return self.report

    def calc_secondary(self, DiffEngine, nodeIDs_unchanged):
        all_tasks = []
        for pair in nodeIDs_unchanged:
            node_init = pair[0]
            node_updated = pair[1]
            print('[TASK] Compare objects with root nodeIDs {}'.format(pair))

            # run component diff
            res = DiffEngine.diff_subgraphs(node_init, node_updated)
            self.report.capture_result_secondary(res)

            # run component diff async
            # task = asyncio.create_task(DiffEngine.diff_subgraphs_async(node_init, node_updated))
            # all_tasks.append(task)
        # tic = time.process_time()
        # result = await asyncio.gather(*all_tasks)
        return self.report
