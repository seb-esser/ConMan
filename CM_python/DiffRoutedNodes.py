""
from pycommon.neo4jConnector import Neo4jConnector

# defs
def GetHashes(label):
	getModel = 'match(n:rootedNode:{})'.format(label)
	open_sub = 'CALL {WITH n'
	removeLabel = 'REMOVE n:{}'.format(label)
	calc_fingerprint = 'with apoc.hashing.fingerprint(n) as hash RETURN hash'
	close_sub = '}'
	add_label_again = 'SET n:{}'.format(label)
	return_results = 'RETURN hash, n.entityType, ID(n)'
	return [getModel, open_sub, removeLabel, calc_fingerprint,close_sub, add_label_again, return_results]

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


# -- ... --

connector = Neo4jConnector()
connector.connect_driver()

label_init = "version20200928T082803"
label_updated = "version20200928T082848"

cypher = []

hash_statement_init = GetHashes(label_init)
hash_statement_updated = GetHashes(label_updated)

cypher_hash_init = connector.BuildMultiStatement(hash_statement_init)
cypher_hash_updated = connector.BuildMultiStatement(hash_statement_updated)

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

# loop over all initial nodes
nodes_deleted = []

for key, val in hashes_init.items():
	if key in hashes_updated.keys():
		print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_updated[key], key))
		# run cypher to connect both nodes 
		cypher_connect = ConnectNodesWithSameHash(hashes_init[key], hashes_updated[key])
		connector.run_cypher_statement(connector.BuildMultiStatement(cypher_connect))
	else: 
		print('\t[RESULT] No match for hashsum {}. Node {} from the initial graph has no matching partner in the updated graph.'.format(key, val))
		nodes_deleted.append(val);

nodes_added = []
# loop over updated nodes
for key, val in hashes_updated.items():
	if key in hashes_init.keys():
		print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_init[key], key))
		# run cypher to connect both nodes 
		cypher_connect = ConnectNodesWithSameHash(hashes_updated[key], hashes_init[key])
		connector.run_cypher_statement(connector.BuildMultiStatement(cypher_connect))
	else: 
		print('\t[RESULT] No match for hashsum {}. Node {} from the updated graph has no matching partner in the initial graph.'.format(key, val))
		nodes_added.append(val)

print('Deleted nodes: ')
for node in nodes_deleted: 
	print('\t Node {}'.format(node))

print('Added nodes: ')
for node in nodes_added: 
	print('\t Node {}'.format(node))