
from IfcGraphInterface.Graph2IfcTranslator import Graph2IfcTranslator
from neo4j_middleware.neo4jConnector import Neo4jConnector

def parse(ts="ts20121017T152740"):
    connector = Neo4jConnector()
    connector.connect_driver()


    # init generator instance
    generator = Graph2IfcTranslator(connector=connector, ts=ts, schema_identifier='IFC2x3')

    # load data into IFC
    generator.generateSPF()

    # save model as IFC SPF file
    generator.save_model('solibri_fromGraph_initial')

    # disconnect driver
    connector.disconnect_driver()

