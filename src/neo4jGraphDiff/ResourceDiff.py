from typing import List

from neo4jGraphDiff.AbsGraphDiff import AbsGraphDiff
from neo4jGraphDiff.Caption.NodeMatchingTable import NodePair
from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum
from neo4jGraphDiff.GraphDelta import GraphDelta
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPath import GraphPath
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeDiffData import NodeDiffData
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class ResourceDiff(AbsGraphDiff):
    """ compares two directed graphlets based on a node diff of nodes and recursively analyses the entire subgraph """

    def __init__(self, connector, label_init, label_updated, config):
        super().__init__(connector, label_init, label_updated, config)

        self.current_prim_init: NodeItem = NodeItem(-1)
        self.current_prim_updated: NodeItem = NodeItem(-1)

        # capture delta
        self.result = GraphDelta(label_init=label_init, label_updated=label_updated)

    def get_delta(self):
        """
        returns the calculated delta
        """
        return self.result

    # public overwrite method requested by abstract superclass AbsGraphDiff
    def diff_subgraphs(self, node_init: NodeItem, node_updated: NodeItem):
        """
        compares the resources under a specified node pair
        node_init: NodeItem
        node_updated: NodeItem
        is_primary_pair: specifies if a new prim node is entered
        """

        # set current prim nodes
        self.current_prim_init = node_init
        self.current_prim_updated = node_updated

        # start recursion on resource structure
        self.__compare_and_continue(node_init, node_updated, indent=0)

        return self.result

    def __compare_and_continue(self, node_init, node_updated, indent=0):
        """
        compares two nodes n_init and n_updated semantically.
        Afterwards, the method searches for the next direct child nodes and detects structural changes.
        """
        # detect changes on property level between both matching nodes
        self.__calc_semantic_delta(node_init, node_updated)

        matching_method = self.configuration.DiffSettings.MatchingType_Childs

        # get children nodes
        children_init = self.get_children_nodes(self.label_init, node_init.id)
        children_updated = self.get_children_nodes(self.label_updated, node_updated.id)

        # apply DiffIgnore -> Ignore nodes if requested
        children_init = self.apply_diff_ignore_nodes(children_init)
        children_updated = self.apply_diff_ignore_nodes(children_updated)

        # leave node?
        if len(children_init) == 0 and len(children_updated) == 0:
            if self.toConsole():
                print("".ljust(indent * 4) + ' leaf node.')
            return

        # calc hashes if necessary for matching method
        if matching_method == MatchCriteriaEnum.OnHash:
            # calc hashes for init and updated
            children_init = self.__get_hashes_of_nodes(self.label_init, children_init, indent)
            children_updated = self.__get_hashes_of_nodes(self.label_updated, children_updated, indent)

        # compare children and raise an dissimilarity if necessary.
        [nodes_unchanged, nodes_added, nodes_deleted] = self.utils.calc_intersection(children_init, children_updated,
                                                                                     matching_method)

        # check if nodes in nodes_unchanged got already matched but a previous subtree analysis
        import copy
        intmed_unc = copy.deepcopy(nodes_unchanged)
        for pair in intmed_unc:
            if NodePair(pair[0], pair[1]) in self.result.node_matching_table.matched_nodes:
                # stop recursion because this node pair was already visited in a previous step
                nodes_unchanged.remove(pair)
            elif self.result.node_matching_table.node_involved_in_nodePair(pair[0]):
                # init node of matched pair was already involved in a matching
                nodes_unchanged.remove(pair)
            elif self.result.node_matching_table.node_involved_in_nodePair(pair[1]):
                # updated node of matched pair was already involved in a matching
                nodes_unchanged.remove(pair)

        if self.toConsole():
            print('')
            print("".ljust(indent * 4) + 'children unchanged: {}'.format(nodes_unchanged))
            print("".ljust(indent * 4) + 'children added: {}'.format(nodes_added))
            print("".ljust(indent * 4) + 'children deleted: {} \n'.format(nodes_deleted))

        if len(nodes_added) != 0 or len(nodes_deleted) != 0:
            # log structural modifications if not yet captured
            for ch in nodes_added:
                # ToDo: check if detected sMod was already logged
                self.result.capture_structure_mod(node_updated, ch, 'added')

            for ch in nodes_deleted:
                self.result.capture_structure_mod(node_init, ch, 'deleted')

        # --- 3 --- loop over all matching child pairs and detect their similarities and differences

        # check the nodes that have the same relationship OR the same EntityType and the same node type: 
        for matchingChildPair in nodes_unchanged:

            for n1, n2 in nodes_unchanged:
                if self.result.node_matching_table.node_pair_in_matching_table(NodePair(n1, n2)):
                    # logged this pair already, continue for loop
                    continue
                else:
                    # log the pair as similar_to
                    self.result.node_matching_table.add_matched_nodes(n1, n2)

            # run recursion for children if "NoChange" or "Modified" happened
            self.__compare_and_continue(matchingChildPair[0], matchingChildPair[1], indent=indent + 1)

        return

    def calc_dict_diff(dict_left: dict, dict_right: dict) -> dict:
        """
        calculates the difference between two dictionaries and returns a dictionary with the differences in apoc.diff style
        @param dict_init: the initial attrs of the node 
        @param node_updated: the updated attrs of the node
        @return: 
        """
        # Same key, different/same value
        different = {}
        inCommon = {}
        for key in dict_left.keys():
            if key in dict_right:
                if dict_left[key] != dict_right[key]:
                    # different value
                    different[key] = {"left": dict_left[key], "right": dict_right[key]}
                else:
                    # same value
                    inCommon[key] = dict_left[key]
        
        # Right only
        rightOnly = {}
        for key in dict_right.keys():
            if not key in dict_left:
                rightOnly[key] = dict_right[key]
                
        # Left only
        leftOnly = {}
        for key in dict_left.keys():
            if not key in dict_right:
                leftOnly[key] = dict_left[key]
        
        # Join dictionaries
        ret_val = {"leftOnly": leftOnly, "inCommon": inCommon, "different": different, "rightOnly": rightOnly}
        return ret_val
    
    def __calc_semantic_delta(self, node_init: NodeItem, node_updated: NodeItem) -> None:
        """
        calculates and captures a semantic modification between two nodes
        @param node_init:
        @param node_updated:
        @return:
        """
        # compare two nodes
        cypher = Neo4jQueryFactory.diff_nodes(node_init.id, node_updated.id)
        raw = self.connector.run_cypher_statement(cypher)

        # delta between both nodes in raw structure
        attr_delta = NodeDiffData.fromNeo4jResponse(raw)

        # apply DiffIgnore on diff delta
        node_diff: NodeDiffData = self.apply_diff_ignore_attributes(attr_delta)

        if self.toConsole():
            print('comparing node {} to node {} after applying DiffIgnore:'.format(node_init.id, node_updated.id))

        # case 1: no modifications on pair
        if node_diff.nodes_are_similar():
            # nodes are similar
            if self.toConsole():
                print('[RESULT]: child nodes match')

        else:
            # log modifications
            root_init = self.current_prim_init
            root_updated = self.current_prim_updated

            if node_init == root_init:
                pattern = GraphPattern(paths=[])
                # ToDo: improve situation if a propertyModification has been applied to a primary node.
                #  Then the construction of a full pattern fails.
            else:
                pattern = self.__get_pattern(root_init.id, node_init.id)

            pmod_list = node_diff.create_pmod_definitions(node_init, node_updated, pattern=pattern)

            # append modifications to delta
            for pm in pmod_list:
                # Note: the modification is captured even though it might be already recognized by another path.
                # please use the unify methods in the GraphDelta class to filter detected modifications afterwards
                self.result.capture_property_mod_instance(pm)

    def __get_hashes_of_nodes(self, label: str, node_list: List[NodeItem], indent=0) -> List[NodeItem]:
        """
        calculates the hash_value sum for each node in a given node list
        @param label: the model identifier
        @param node_list: a list of nodes the hash value should be calculated
        @param indent: printing stuff (might be removed soon)
        @return:
        """

        ignore_attrs = self.configuration.DiffSettings.diffIgnoreAttrs  # list of strings
        # calc corresponding hash_value
        for node in node_list:
            # calc hash_value of current node
            cypher_hash = Neo4jQueryFactory.get_hash_by_nodeId(label, node.id, ignore_attrs)
            hash_value = self.connector.run_cypher_statement(cypher_hash)[0][0]

            node.set_hash(hash_value)

        if self.toConsole():
            print("".ljust(indent * 4) + 'Calculated hashes for model >> {} <<:'.format(label))
            for node in node_list:
                print("".ljust(indent * 4) + '\t NodeID: {:<4} \t hash_value: {}'.format(node.id, node.hash_value))

        return node_list

    def __get_pattern(self, root_node_id: int, current_node_id: int) -> GraphPattern:
        """

        @param root_node_id:
        @param current_node_id:
        @return:
        """
        cy = Neo4jQueryFactory.get_directed_path_by_nodeId(node_id_start=root_node_id, node_id_target=current_node_id)
        res = self.connector.run_cypher_statement(cy)
        try:
            path = GraphPath.from_neo4j_response(res)
            pattern = GraphPattern(paths=[path])
            return pattern
        except:
            print('Tried to query a graph pattern. DB response was empty. NodeInit_ID: {} NodeUpdt_ID: {}'
                  .format(root_node_id, current_node_id))
            return GraphPattern([])
