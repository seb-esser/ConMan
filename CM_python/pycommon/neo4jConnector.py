from neo4j import GraphDatabase
import json

class Neo4jConnector:

    # member variables
    password = "password"
    uri = "bolt://localhost:7687"
    my_driver = []

    # constructor
    def __init__(self):
        print("Initialized new Connector instance.")
        pass

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

    def run_cypher_statement(self, statement, postStatement=None):

        #returnTypes = {
        #    'getId' : (lambda record: result = record['ID(n)'] ), 
        #    'getGlobalId' : (lambda record: result = record['globalId'] )
        #    }
        try:
            with self.my_driver.session() as session:
                with session.begin_transaction() as tx:
                    print("[neo4j_connector] Running query: " + str(statement)[:50] + '...')
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
                print('[neo4j_connector] Received response. ')
                return return_val

        except :
            print('[neo4j_connector] something went wrong. Check the neo4j connector. ')
            
       



    def disconnect_driver(self):
        self.my_driver.close()
        print('Driver disconnected.')


    # constructs a multi statement cypher command
    def BuildMultiStatement(self, cypherCMDs):
         return ' '.join(cypherCMDs)