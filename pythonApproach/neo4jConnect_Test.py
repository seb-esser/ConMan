from neo4j import GraphDatabase, basic_auth

password = "password"
uri = "bolt://localhost:7687"
my_driver = GraphDatabase.driver(uri, auth=("neo4j", password), encrypted=False)

with my_driver.session() as session:
    with session.begin_transaction() as tx:
        for record in tx.run("MATCH (n:Storey) RETURN n"):
            print(record)


my_driver.close()

