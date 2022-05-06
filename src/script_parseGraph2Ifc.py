
from IfcGraphInterface.Graph2IfcTranslator import Graph2IfcTranslator
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

ts = "ts20210623T091749"

# init generator instance
generator = Graph2IfcTranslator(connector=connector, ts=ts)

# load data into IFC
generator.generateSPF()

# save model as IFC SPF file
generator.save_model('solibri_fromGraph_initial')

# disconnect driver
connector.disconnect_driver()

