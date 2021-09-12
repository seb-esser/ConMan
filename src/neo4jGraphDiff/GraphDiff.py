from neo4jGraphDiff.Caption.DeltaReporter import DeltaReporter
from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.ConnectionNodeDiff import ConnectionNodeDiff
from neo4jGraphDiff.PrimaryNodeDiff import PrimaryNodeDiff
from neo4jGraphDiff.ResourceDiff import ResourceDiff
from neo4j_middleware.neo4jConnector import Neo4jConnector


class GraphDiff:
    def __init__(self, label_init: str, label_updated: str):
        self.config = Configuration.rel_type_config()
        print(self.config)
        print(self.config.DiffSettings)
        self.label_init = label_init
        self.label_updated = label_updated

        self.report = DeltaReporter(ts_init=label_init, ts_updated=label_updated, usedConfig=self.config)

    def run_diff(self, connector: Neo4jConnector):
        cypher = []

        # 1: Check base structure of rooted nodes

        print(' ROOT DIFF \n')

        # diff primary node sets
        rootedNodeDiff = PrimaryNodeDiff(connector, self.config)
        [nodes_unchanged, nodes_added, nodes_deleted] = rootedNodeDiff.diff_primary_nodes(self.label_init,
                                                                                          self.label_updated)

        # save results to report
        self.report.capture_result_primary([nodes_unchanged, nodes_added, nodes_deleted])

        print(' CONNECTION NODE DIFF \n')

        # diff connection nodes
        connectionNodeDiff = ConnectionNodeDiff(connector=connector,
                                                label_init=self.label_init,
                                                label_updated=self.label_updated)
        [conNodeIDs_unchanged, conNodeIDs_added, conNodeIDs_deleted] = connectionNodeDiff.diff_connectionNodes()

        # save results to report
        self.report.capture_result_con_nodes([conNodeIDs_unchanged, conNodeIDs_added, conNodeIDs_deleted])

        print('\n COMPONENT DIFF \n')

        # 2: Check sub-graphs for each rooted node

        self.calc_secondary(connector=connector, nodes_unchanged=nodes_unchanged)

        return self.report

    def calc_secondary(self, connector: Neo4jConnector, nodes_unchanged):

        all_tasks = []
        for pair in nodes_unchanged:
            DiffEngine = ResourceDiff(connector=connector,
                                      label_init=self.label_init,
                                      label_updated=self.label_updated,
                                      config=self.config)

            node_init = pair[0]
            node_updated = pair[1]
            print('[TASK] Compare objects with root nodeIDs {}'.format(pair))

            # run component diff
            DiffEngine.diff_subgraphs(node_init, node_updated)

            # get delta
            res = DiffEngine.get_delta()

            self.report.capture_result_secondary(res)

            # run component diff async
            # task = asyncio.create_task(DiffEngine.diff_subgraphs_async(node_init, node_updated))
            # all_tasks.append(task)
        # tic = time.process_time()
        # delta = await asyncio.gather(*all_tasks)
        return self.report
