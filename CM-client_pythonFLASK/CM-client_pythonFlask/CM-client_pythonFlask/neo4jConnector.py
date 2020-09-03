from neo4j import GraphDatabase


class Neo4jConnector:

    # member variables
    password = "0000"
    uri = "bolt://localhost:7687"
    my_driver = []

    # constructor
    def __init__(self):
        print("Initialized new Connector instance.")

    # methods
    def connect_driver(self):
        try:
            self.my_driver = GraphDatabase.driver(self.uri, auth=("neo4j", self.password), encrypted=False)
        except self.my_driver:
            print("Oops!  Connection failed.  Try again...")
        
            

    def test_connection(self):
        with self.my_driver.session() as session:
            with session.begin_transaction() as tx:
                for record in tx.run("MATCH (n) RETURN n LIMIT 25"):
                    print(record)

    def run_cypher_statement(self, statement):
        with self.my_driver.session() as session:
            with session.begin_transaction() as tx:
                print("\n -- Performing: " + statement)
                res = tx.run(statement)
                for ans in res:
                    print(ans)
                return res

    def disconnect_driver(self):
        self.my_driver.close()
        print('Driver disconnected.')