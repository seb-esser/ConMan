
from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4jGraphAnalysis.AdjacencyAnalyser import AdjacencyAnalyser

# init connection
connector = Neo4jConnector()
connector.connect_driver()

## cuboid sample with height elevation
label_init = "ts20210119T085408"
label_updated = "ts20210119T085409"

# do magic
analysis_engine = AdjacencyAnalyser(connector)
adj_mtx = analysis_engine.get_adjacency_matrix_byHashsums(label_init)



# close connection 
connector.disconnect_driver()



