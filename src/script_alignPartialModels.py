from neo4j_middleware.neo4jConnector import Neo4jConnector


def main():
    connector = Neo4jConnector()
    connector.connect_driver()

    ts_1 = ""
    ts_2 = ""

    # align based on GUIDs
    cy = """
    MATCH (n:PrimaryNode:{}) 
    MATCH (m:PrimaryNode:{}) WHERE m.GlobalId = n.GlobalId
    
    RETURN n.EntityType, n.Name,  m.EntityType,  m.Name
    """.format(ts_1, ts_2)

    connector.run_cypher_statement(cy)

    connector.disconnect_driver()


if __name__ == "__main__":
    main()
