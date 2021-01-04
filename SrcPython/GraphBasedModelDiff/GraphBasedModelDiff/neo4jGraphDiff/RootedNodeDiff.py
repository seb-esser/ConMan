
from .DiffUtilities import DiffUtilities
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils

class RootedNodeDiff:
	
	def __init__(self): 
		pass

	def compareRootedNodes(self, connector, label_init, label_updated):
		hash_statement_init = DiffUtilities.GetHashes(label_init)
		hash_statement_updated = DiffUtilities.GetHashes(label_updated)

		cypher_hash_init = neo4jUtils.BuildMultiStatement(hash_statement_init)
		cypher_hash_updated = neo4jUtils.BuildMultiStatement(hash_statement_updated)

		res_init = connector.run_cypher_statement(cypher_hash_init)
		res_updated = connector.run_cypher_statement(cypher_hash_updated)

		hashes_init = self.extractHashes(res_init)
		hashes_updated = self.extractHashes(res_updated)


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
		nodes_deleted = []
		nodes_added = []

		# loop over all initial nodes
		
		print('\n[TASK] Looking for hashes from the initial graph... \n')
		for key, val in hashes_init.items():
			# print('\t hash: {}'.format(key))
			if key in hashes_updated.keys():
				# print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_updated[key], key))
		
				if key not in nodes_unchanged: 
					nodes_unchanged[key] = (val, hashes_updated[key])
		
				
				# connector.run_cypher_statement(neo4jUtils.BuildMultiStatement(cypher_connect))
			else: 
				# print('\t[RESULT] No match for hashsum {}. Node {} from the initial graph has no matching partner in the updated graph.'.format(key, val))
				nodes_deleted.append(val);

		

		print('\n[TASK] Looking for hashes from the updated graph... \n')
		# loop over updated nodes
		for key, val in hashes_updated.items():
			print('\t hash: {}'.format(key))
			if key in hashes_init.keys():
				# print('\t[RESULT] Link {} with {} based on common hashsum {}'.format(val, hashes_init[key], key))
		
				if key not in nodes_unchanged: 
					nodes_unchanged[key] = (val, hashes_updated[key])

				
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

	def compareRootedNodeRelationships(self):
		hash_statement_init = DiffUtilities.GetHashes(label_init)
		hash_statement_updated = DiffUtilities.GetHashes(label_updated)

		cypher_hash_init = neo4jUtils.BuildMultiStatement(hash_statement_init)
		cypher_hash_updated = neo4jUtils.BuildMultiStatement(hash_statement_updated)

		res_init = connector.run_cypher_statement(cypher_hash_init)
		res_updated = connector.run_cypher_statement(cypher_hash_updated)

		hashes_init = self.extractHashes(res_init)
		hashes_updated = self.extractHashes(res_updated)

		

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




	# private helper functions
	def extractHashes(self, result): 
		hashes = []
		nodeIds = []
		for res in result: 
			hash = res[0]
			nodeId = res[2]
			hashes.append(hash)
			nodeIds.append(nodeId)
	
		return_dict = dict(zip(hashes, nodeIds))

		return return_dict


