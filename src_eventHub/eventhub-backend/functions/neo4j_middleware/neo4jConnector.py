
from neo4j import GraphDatabase


class Neo4jConnector:
    """ handles the connection to a given neo4j database """
    # member variables
    password = "password"
    uri = "bolt://localhost:7687"
    my_driver = []

    # constructor
    def __init__(self):
        pass

    # methods
    def connect_driver(self):
        """
        creates a new connection to the database
        @return:
        """
        try:
            self.my_driver = GraphDatabase.driver(self.uri, auth=("neo4j", self.password), encrypted=False)
        except self.my_driver:

            raise Exception("Oops!  Connection failed.  Try again...")

    def run_cypher_statement(self, statement, postStatement = None):
        """
        executes a given cypher statement and does some post processing if stated
        @statement: cypher command
        @postStatement: post processing of response
        @return
        """

        try:
            with self.my_driver.session() as session:
                with session.begin_transaction() as tx:
                    res = tx.run(statement)

                    return_val = []

                    if postStatement != None:
                        for record in res:
                            # print(record[postStatement])
                            return_val.append(record[postStatement])

                    else:
                        for record in res:
                            # print(record)
                            return_val.append(record)

                return return_val

        except:

            print('[neo4j_connector] something went wrong. Check the neo4j connector. ')
            print('[neo4j_connector] Tried to execute cypher statement >> {} <<'.format(statement))
            print('[neo4j_connector] Possible issues: ' +
                         '\t Incorrect cypher statement' +
                         '\t Missing packages inside the graph database \n')
            raise Exception('Error in neo4j Connector.')

    def disconnect_driver(self):
        """
        disconnects the connector instance
        @return:
        """
        self.my_driver.close()


