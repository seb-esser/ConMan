""" """ 

import numpy as np

from pycommon.neo4jConnector import Neo4jConnector

# --- defs --- 
def GetAdjacencyMatrix(label):	
	match = 'MATCH (n:rootedNode:{}) WITH collect(n) AS Nodes'.format(label)

	for1 = 'WITH [n IN Nodes |'
	for2 = '[m IN Nodes |'

	case = 'CASE size((n)--(m))	'
	ifState = 'WHEN 0 THEN 0'
	elseState = 'ELSE 1'
	endif = 'END ]] AS AdjacencyMatrix'
	ret = 'RETURN AdjacencyMatrix'

	return [match, for1, for2, case, ifState, elseState, endif, ret]

	# from https://community.neo4j.com/t/adjacency-matrix-using-cypher-query/16462 

# --- script -- 
connector = Neo4jConnector()
connector.connect_driver()

label_init = "version20200928T082803"

# run query
cypher = connector.BuildMultiStatement(GetAdjacencyMatrix(label_init))
adja_raw_init = connector.run_cypher_statement(cypher)


adj_mtx = adja_raw_init[0][0]
np_mtx = np.matrix(adj_mtx)



