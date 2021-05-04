

import logging

from neo4j import GraphDatabase


class Neo4jConnector:

    # member variables
    password = "password"
    uri = "bolt://localhost:7687"
    my_driver = []

    # constructor
    def __init__(self, writeToConsole=True, writeToLogFile=False):
        print("Initialized new Connector instance.")
        self.ToConsole = writeToConsole
        self.ToLogFile = writeToLogFile

    # methods
    def connect_driver(self):
        try:
            self.my_driver = GraphDatabase.driver(self.uri, auth=("neo4j", self.password), encrypted=False)
        except self.my_driver:
            raise Exception("Oops!  Connection failed.  Try again...")       
            

    def test_connection(self):
        with self.my_driver.session() as session:
            with session.begin_transaction() as tx:
                for record in tx.run("MATCH (n) RETURN n LIMIT 25"):
                    print(record)

    def run_cypher_statement(self, statement, postStatement=None):
        """ executes a given cypher statement and does some post processing if stated """
      
        try:
            with self.my_driver.session() as session:
                with session.begin_transaction() as tx:
                    if self.ToConsole:
                        print("[neo4j_connector] Running query: " + str(statement)[:80] + '...')
                    if self.ToLogFile:
                        logging.info("Running query:" +str(statement))
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
                if self.ToConsole:
                    print('[neo4j_connector] Received response. ')
                return return_val

        except :
            print('[neo4j_connector] something went wrong. Check the neo4j connector. ')
            print('[neo4j_connector] Tried to execute cypher statement >> {} <<'.format(statement) )
            print('[neo4j_connector] Possible issues: ' + 
                    '\t Incorrect cypher statement' + 
                    '\t Missing packages inside the graph database \n')
            raise Exception('Error in neo4j Connector.')

    def disconnect_driver(self):
        self.my_driver.close()
        print('Driver disconnected.')


    # constructs a multi statement cypher command
    def BuildMultiStatement(self, cypherCMDs):
         return ' '.join(cypherCMDs)