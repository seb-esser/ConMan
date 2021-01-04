
""

# import numpy as np

from neo4j_middleware.neo4jConnector import Neo4jConnector
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

# defs
def GetHashes(label):
	getModel = 'MATCH(n:rootedNode:{})'.format(label)
	open_sub = 'CALL {WITH n'
	removeLabel = 'REMOVE n:{}'.format(label)
	calc_fingerprint = 'with apoc.hashing.fingerprint(n, {}) as hash RETURN hash'.format('["p21_id"]')
	close_sub = '}'
	add_label_again = 'SET n:{}'.format(label)
	return_results = 'RETURN hash, n.entityType, ID(n)'
	return [getModel, open_sub, removeLabel, calc_fingerprint, close_sub, add_label_again, return_results]

def ConnectNodesWithSameHash(NodeIdFrom, NodeIdTo):
	fromNode = 'MATCH (s) WHERE ID(s) = {}'.format(NodeIdFrom)
	toNode = 'MATCH (t) WHERE ID(t) = {}'.format(NodeIdTo)
	merge = 'MERGE (s)-[r:{}]->(t)'.format('IS_EQUAL_TO')
	return [fromNode, toNode, merge]

def RemoveNodeConnectionsCreatedByHash():
	match = 'Match(n)-[r:IS_EQUAL_TO]->(p)'
	delete = 'delete r'


def extractHashes(result): 
	hashes = []
	nodeIds = []
	for res in result: 
		hash = res[0]
		nodeId = res[2]
		hashes.append(hash)
		nodeIds.append(nodeId)
	
	return_dict = dict(zip(hashes, nodeIds))

	return return_dict

def GetAdjacencyMatrixByNodeId(i, j):	
	#match1 = 'MATCH (n) WHERE ID(n) = {}'.format(i)
	#match2 = 'MATCH (m) WHERE ID(m) = {}'.format(j)		
	#case = 'CASE size((n)--(m))'
	#ifState = 'WHEN 0 THEN 0'
	#elseState = 'ELSE 1'
	#endif = 'END AS adjacent'
	#ret = 'RETURN adjacent'
	match1 = 'MATCH (n) WHERE ID(n) = {}'.format(i)
	match2 = 'MATCH (m) WHERE ID(m) = {}'.format(j)
	ret = 'RETURN ID(n), ID(m), EXISTS ((n)--(m)) as is_connected'

	return [match1, match2, ret]

def GetSubGraphOfNode(): 
	match = 'MATCH path  = (n:IfcAlignment)-[*0..100]->(p)' 
	ret = 'RETURN p'

	return [match, ret]

# -- ... --

connector = Neo4jConnector(False, False)
connector.connect_driver()

label_init = "ts20200202T105551"
label_updated = "ts20200204T105551"

cypher = []

hash_statement_init = GetHashes(label_init)
hash_statement_updated = GetHashes(label_updated)

cypher_hash_init = neo4jUtils.BuildMultiStatement(hash_statement_init)
cypher_hash_updated = neo4jUtils.BuildMultiStatement(hash_statement_updated)

res_init = connector.run_cypher_statement(cypher_hash_init)
res_updated = connector.run_cypher_statement(cypher_hash_updated)

hashes_init = extractHashes(res_init)
hashes_updated = extractHashes(res_updated)


# output
print('\n')
print('[DiffCalc] HASHES for initial model: ')
for res in res_init:
	print(res)
print('\n')
print('[DiffCalc] HASHES for updated model: ')
for res in res_updated:
	print(res)


# compare hashes: 

# loop over initial nodes

print('\n[DiffCalc] Mapping the hashcodes between initial and updated: ')

nodes_unchanged = {}

# loop over all initial nodes
nodes_deleted = []
print('\n[TASK] Looking for hashes from the initial graph... \n')
for key, val in hashes_init.items():
	# print('\t hash: {}'.format(key))
	if key in hashes_updated.keys():
		# print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_updated[key], key))
		
		if key not in nodes_unchanged: 
			nodes_unchanged[key] = (val, hashes_updated[key])
		
		# run cypher to connect both nodes 
		cypher_connect = ConnectNodesWithSameHash(hashes_init[key], hashes_updated[key])
		# connector.run_cypher_statement(neo4jUtils.BuildMultiStatement(cypher_connect))
	else: 
		# print('\t[RESULT] No match for hashsum {}. Node {} from the initial graph has no matching partner in the updated graph.'.format(key, val))
		nodes_deleted.append(val);

nodes_added = []

print('\n[TASK] Looking for hashes from the updated graph... \n')
# loop over updated nodes
for key, val in hashes_updated.items():
	print('\t hash: {}'.format(key))
	if key in hashes_init.keys():
		# print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_init[key], key))
		
		if key not in nodes_unchanged: 
			nodes_unchanged[key] = (val, hashes_updated[key])

		# run cypher to connect both nodes 
		cypher_connect = ConnectNodesWithSameHash(hashes_updated[key], hashes_init[key])
		# connector.run_cypher_statement(neo4jUtils.BuildMultiStatement(cypher_connect))
	else: 
		# print('\t[RESULT] No match for hashsum {}. Node {} from the updated graph has no matching partner in the initial graph.'.format(key, val))
		nodes_added.append(val)

print('Results:')
print('\t Deleted nodes: ')
for node in nodes_deleted: 
	print('\t Node {}'.format(node))

print('\n \t Added nodes: ')
for node in nodes_added: 
	print('\t Node {}'.format(node))

print('\n \t Unchanged nodes: ')
for key, val in nodes_unchanged.items(): 
	print('\t Hash {:<25} \t Node_Id {:<5} \t NodeId: {}'.format( key, val[0], val[1]))


print('\n ---- ---- ')

hashes_init_list = list(hashes_init.keys()); 
hashes_init_list.sort()

hashes_updated_list = list(hashes_updated.keys()); 
hashes_updated_list.sort()

adj_init = []

# calc adjacency for initial
def calcAdjacencyMatrix(hashes_sorted, hash_dict):
	adj = []
	for hash_i in hashes_sorted: 
		node_i = hash_dict[hash_i]
		row = []
		for hash_j in hashes_sorted: 
			node_j = hash_dict[hash_j]
			cy = GetAdjacencyMatrixByNodeId(node_i, node_j)
			res = connector.run_cypher_statement(neo4jUtils.BuildMultiStatement(cy), 'is_connected')
			
			if res[0] == False: 
				row.append(0)
			else: 
				row.append(1)
	
		adj.append(row)
	return adj

adj_init = calcAdjacencyMatrix(hashes_init_list, hashes_init)
adj_updated = calcAdjacencyMatrix(hashes_updated_list, hashes_updated)


	
def print_grid(adj, hash_list): 
	i = 0
	for row in adj:
		# print('{0:<30}'.format(hash_list[i]))
		j = 0
		for col in row:
			# print('{0:<30}'.format(hash_list[j]))
			print(col,end='\t')
			j +=1
		print()
		i +=1
	print('\n\n')

print('[TASK] Compare edges by adjacency matrix')

print('Adjacency Mtx initial model - sorted by hashes:')
i = 0
for hash in hashes_init_list: 
	print('row|col {} : {}'.format(i, hash))
	i +=1
print()
print_grid(adj_init, hashes_init_list)

print('Adjacency Mtx updated model - sorted by hashes:')
i = 0
for hash in hashes_updated_list: 
	print('row|col {} : {}'.format(i, hash))
	i +=1
print()
print_grid(adj_updated, hashes_updated_list)
