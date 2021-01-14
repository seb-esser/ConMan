
from .DiffUtilities import DiffUtilities
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jQueryUtils
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory 
from neo4j_middleware.NodeData import NodeData 


class RootedNodeDiff:
	""" """
	def __init__(self, connector, toConsole = True): 
		self.toConsole = toConsole
		self.utils = DiffUtilities()
		self.connector = connector
		pass

	def diffRootedNodes(self, label_init, label_updated, attr_ignore_list):
		""" """
		
		# retrieve nodes
		nodes_init = self.__getRootedNodes(label_init)
		nodes_updated = self.__getRootedNodes(label_updated)

		for node in nodes_init: 
			cy = neo4jQueryFactory.GetHashByNodeId(label_init, node.id, attr_ignore_list) 
			res = self.connector.run_cypher_statement(cy)
			node.hash = res[0][0]

		for node in nodes_updated: 
			cy = neo4jQueryFactory.GetHashByNodeId(label_updated, node.id, attr_ignore_list)
			res = self.connector.run_cypher_statement(cy)
			node.hash = res[0][0]


		[nodes_unchanged, nodes_added, nodes_deleted] = self.utils.CompareNodesByHash(nodes_init, nodes_updated, considerRelType=False)
		
		if self.toConsole: 
			print('Detected unchanged rooted nodes: {}'.format(nodes_unchanged))
			print('Added nodes: {}'.format(nodes_added))
			print('Deleted nodes: {}'.format(nodes_deleted))

		return [nodes_unchanged, nodes_added, nodes_deleted]

	def compareRootedNodeRelationships(self):
		""" """
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
		


	def __getHashesOfRootedNodes(self, label):
		cy = neo4jQueryFactory.GetHashesByLabel(label)
		raw = self.connector.run_cypher_statement(cy)
		return self.__extractHashes(raw)
		

	def __extractHashes(self, result): 
		nodes = []
		for res in result: 
			node = NodeData(res[0],None, res[1])
			node.setHash(res[2])
			nodes.append(node)
	
		return nodes

	def __getRootedNodes(self, label): 
		cy = neo4jQueryFactory.GetRootedNodes(label)
		raw = self.connector.run_cypher_statement(cy)

		# unpack neo4j response into a list if NodeData instances
		res = NodeData.fromNeo4jResponseWouRel(raw)

		return res

