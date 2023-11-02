""" package import """
import datetime
import logging
import time

""" class import """
from neo4j_middleware.neo4jConnector import Neo4jConnector
from CityGMLGraphInterface.CityGML2GraphTranslator import CityGMLGraphGenerator

# --- Script ---

# init logging
current_date_and_time = datetime.datetime.now()
logging.basicConfig(filename='{}.neo4j-query-log.log', level=logging.INFO)
logging.info('Started')

def main():
    print('Parsing Ifc StepP21 model to Neo4j.... \n')
    print('connecting to neo4j database... ')
    connector = Neo4jConnector()
    connector.connect_driver()
    
    paths = ['./00_sampleData/CityGML/FZKHaus/FZKHausLoD4.gml']

    for p in paths:
        print(p)

    print('Starting to generate graphs...')
    amount = len(paths)
    start = time.perf_counter()
    
    for idx, path in enumerate(paths):
        # parse model
        generator = CityGMLGraphGenerator(connector, path)
        print('Generating Graph {}/{}'.format(idx + 1, amount))
        generator.generateGraph()
    finish = time.perf_counter()
    print('\n 100% done. Graphs generated. Finished in {} seconds.'.format(round(finish-start, 2)))
    # disconnect from database 
    connector.disconnect_driver()

if __name__ == '__main__':
    main()