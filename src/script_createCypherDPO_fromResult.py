from PatchManager.DPOService import DPOService
from neo4j_middleware.neo4jConnector import Neo4jConnector


def main():
    ts_init = "ts20210623T091748"
    ts_updated = "ts20210623T091749"

    connector = Neo4jConnector()
    connector.connect_driver()

    service = DPOService(ts_init=ts_init, ts_updated=ts_updated)
    update_patch = service.generate_DPO_patch(connector=connector)

    # visualize results
    # update_patch.operations[0].plot_patterns()

    # finally disconnect
    connector.disconnect_driver()
    return update_patch


if __name__ == "__main__":
    main()
