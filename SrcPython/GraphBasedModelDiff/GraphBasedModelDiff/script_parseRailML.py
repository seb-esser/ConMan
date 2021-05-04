
""" package import """
import logging

""" class import """
from neo4j_middleware.railML_neo4jMapper import railML_neo4jmapper
from neo4j_middleware.neo4jConnector import Neo4jConnector

# --- defs ---

def parseModel(connector, path): 

	label = "ts20210211121212"

	## DEBUG ONLY! delete entire graph: 
	print('DEBUG INFO: entire graph labeled with >> {} << gets deleted'.format(label))
	connector.run_cypher_statement('MATCH(n:{}) DETACH DELETE n'.format(label))


	# init mapper
	mapper = railML_neo4jmapper(connector, label , path, None)

	# map root structure
	mapper.mapRootedEntities()

	# map resources
	mapper.mapResourceEntities()
	




	# --- Script --- 

# init logging
logging.basicConfig(filename='myapp.log', level=logging.INFO)
logging.info('Started')

print('Parsing RailML model to Neo4j.... \n')
print('connecting to neo4j database... ')
connector = Neo4jConnector(False, True)
connector.connect_driver()

path = './00_sampleData/RailML_xml/railML_SimpleExample_v11_railML3-1_04.xml'
paths = [path]

for path in paths: 
	# parse model
	parseModel(connector, path)


# disconnect from database
connector.disconnect_driver()

