


from neo4jGraphAnalysis.SCC import SccDetector
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector(False, False)
connector.connect_driver()

label_init = "ts20210106T110329"
label_updated = "ts20210106T110250"

detector = SccDetector(connector, label_init, True)
detector.performSCC()
# detector.evaluateResults()

connector.disconnect_driver()

