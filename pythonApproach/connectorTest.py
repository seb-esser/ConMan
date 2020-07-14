# import connector class
from neo4jConnector import Neo4jConnector

# init connector instance with constructor
connector = Neo4jConnector()

# connect driver
connector.connect_driver()

# test connection by querying some data from the database
connector.run_cypher_statement("Match(n:Storey) return n")


# disconnect driver
connector.disconnect_driver()
