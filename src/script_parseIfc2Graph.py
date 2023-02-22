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


def main():
    print('Parsing Ifc StepP21 model to Neo4j.... \n')
    print('connecting to neo4j database... ')
    connector = Neo4jConnector()
    connector.connect_driver()

    # # These lines all filepaths in the directory 'dir'
    # dir = './00_sampleData/IFC_stepP21/**/*.ifc'
    # paths = []
    # for filepath in glob.glob(dir, recursive=True):
    #    paths.append(filepath)
    # print(paths)

    paths = ['./00_sampleData/IFC_stepP21/wand_tuer/01_Wand_single-guidsMod.ifc',
             # './00_sampleData/IFC_stepP21/wand_tuer/02_Wand_mitTuer-guidsMod.ifc'
             ]

    for p in paths:
        print(p)

    print('Starting to generate graphs...')
    amount = len(paths)
    start = time.perf_counter()
    for idx, path in enumerate(paths):
        # parse model
        graph_generator = IFCGraphGenerator(connector, path, None)
        print('Generating Graph %d/%d' % (idx + 1, amount))
        graph_generator.generateGraph()
    finish = time.perf_counter()
    print('100% done. Graphs generated. Finished in {} seconds.'.format(round(finish - start, 2)))

    print("Performing post-processing: Remove layer assignments and styled items ")

    cy = 'MATCH p = (n{EntityType:"IfcStyledItem"})-[r:rel]->(s:SecondaryNode) DELETE r'
    connector.run_cypher_statement(cy)

    cy = 'MATCH p = (n{EntityType:"IfcPresentationLayerAssignment"})-[r:rel]->(s:SecondaryNode) DELETE r'
    connector.run_cypher_statement(cy)

    print("Post-processing done. ")

    # disconnect from database
    connector.disconnect_driver()


if __name__ == '__main__':
    main()
