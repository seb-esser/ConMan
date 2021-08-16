

from IfcGraphInterface.Graph2IfcTranslator import Graph2IfcTranslator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

ts = "ts20200202T105551"

# init generator instance
generator = Graph2IfcTranslator(connector=connector, ts=ts)

# load data into IFC
generator.generateSPF()

# save model as IFC SPF file
generator.save_model('sleeper_new')

# disconnect driver
connector.disconnect_driver()

