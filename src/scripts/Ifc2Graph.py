""" package import """
import logging
import time

""" class import """
from IfcGraphInterface.Ifc2GraphTranslator import IFCGraphGenerator
from neo4j_middleware.neo4jConnector import Neo4jConnector

# --- Script ---

# init logging
logging.basicConfig(filename='myapp.log', level=logging.INFO)
logging.info('Started')

def parse(paths):
    # Init connector
    connector = Neo4jConnector()
    connector.connect_driver()

    amount = len(paths)
    start = time.perf_counter()
    
    for idx, path in enumerate(paths):
        # parse model
        graphGenerator = IFCGraphGenerator(connector, path, None)
        print('[IFC_P21] Generating Graph %d/%d' % (idx + 1, amount))
        graphGenerator.generateGraph()
    
    finish = time.perf_counter()
    print('[IFC_P21] 100% done. Graphs generated. Finished in {} seconds.'.format(round(finish-start, 2)))
    # disconnect from database
    connector.disconnect_driver()
