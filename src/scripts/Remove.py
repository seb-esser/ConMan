from neo4j_middleware.neo4jConnector import Neo4jConnector


def remove(timestamp: str):
    connector = Neo4jConnector()
    connector.connect_driver()

    cy = "MATCH (n:{} ) DETACH DELETE n RETURN COUNT(n)".format(timestamp)
    raw = connector.run_cypher_statement(cy)
    print("Removed {} nodes from graph database".format(raw[0][0]))

    connector.disconnect_driver()


if __name__ == "__main__":
    ts = input("~rm: Specify timestamp\n")
    remove(timestamp=ts)
