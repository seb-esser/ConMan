from neo4j_middleware.neo4jConnector import Neo4jConnector


def align_by_guid(connector):
    ts_1 = ""
    ts_2 = ""

    # align based on GUIDs
    cy = """
        MATCH (n:PrimaryNode:{}) 
        MATCH (m:PrimaryNode:{}) WHERE m.GlobalId = n.GlobalId
        MERGE (n)-[:ALIGNED{AlignmentType: ''ByGuid''}]-(m) 
        """.format(ts_1, ts_2)
    connector.run_cypher_statement(cy)


def align_by_ito_result(connector):
    pass


def align_by_spatial_structure(connector):
    pass


def main():
    connector = Neo4jConnector()
    connector.connect_driver()

    # by guid
    align_by_guid(connector)

    # by solibri
    align_by_ito_result(connector)

    connector.disconnect_driver()


if __name__ == "__main__":
    main()
