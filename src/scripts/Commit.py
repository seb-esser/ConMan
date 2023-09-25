from PatchManager.PatchBundle import PatchBundle
from PatchManager.GraphPatchService import GraphPatchService
from neo4jGraphDiff.GraphDiff import GraphDiff
from neo4j_middleware.BucketManager.BucketUtility import BucketUtility
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


def commit(commit_message: str):
    """
    commit function that compares graphs and produce corresponding patches
    """

    if commit_message is None or commit_message == "":
        raise Exception("Please specify a commit message. ")

    # connect to db
    connector = Neo4jConnector()
    connector.connect_driver()

    # init patch bundle
    bundle = PatchBundle(message=commit_message)

    buckets = BucketUtility().get_buckets()

    for bucket in buckets:
        last_committed = bucket.get_last_committed_version()
        most_recent = bucket.get_most_recent_version()

        # run diff
        # get topmost entry nodes
        raw_init = connector.run_cypher_statement(
            """
            MATCH (n:PrimaryNode:{} {{EntityType: "IfcProject"}})
            RETURN n
            """.format(last_committed.timestamp))
        raw_updated = connector.run_cypher_statement(
            """
            MATCH (n:PrimaryNode:{} {{EntityType: "IfcProject"}})
            RETURN n
            """.format(most_recent.timestamp))

        entry_init: NodeItem = NodeItem.from_neo4j_response(raw_init)[0]
        entry_updated: NodeItem = NodeItem.from_neo4j_response(raw_updated)[0]

        pDiff = GraphDiff(connector=connector, ts_init=last_committed.timestamp, ts_updated=most_recent.timestamp)
        delta = pDiff.diff_subgraphs(entry_init, entry_updated)

        # connect equivalent nodes
        pDiff.build_equivalent_to_edges()

        # create and store patch
        service = GraphPatchService.from_existing_delta(delta=delta, connector=connector)
        print("[INFO] Generate Patch for bucket {}".format(bucket.GlobalId))
        patch = service.generate_patch()

        bundle.patches.append(patch)

    # save bundle
    service = GraphPatchService(connector=connector).save_patch_bundle_to_json(bundle)

    # disconnect
    connector.disconnect_driver()


if __name__ == "__main__":
    commit_msg = input("Enter commit message: ")
    commit(commit_message=commit_msg)
