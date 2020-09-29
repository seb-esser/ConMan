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
	return_results = 'RETURN hash, n.EntityType'
	return [getModel, open_sub, removeLabel, calc_fingerprint,close_sub, add_label_again, return_results]


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

res_init = connector.run_cypher_statement(cypher_hash_init, 'hash')
res_updated = connector.run_cypher_statement(cypher_hash_updated, 'hash')

print('\n --- HASHES for initial model: ')
for res in res_init:
	print(res)
print('\n')
print('\n --- HASHES for updated model: ')
for res in res_updated:
	print(res)




