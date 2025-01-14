from typing import List

from neo4jGraphDiff.AbsGraphDiff import AbsGraphDiff
from neo4jGraphDiff.Caption.NodeMatchingTable import NodePair
from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum
from neo4jGraphDiff.GraphDelta import GraphDelta
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.EdgeItem import EdgeItem
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

    def get_delta(self) -> GraphDelta:
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
        # ToDo: Ticket "Improve Diff by Isomorphism appraoches": implement startpoint of isomorphism check here
        # if not self.check_isomorphism():
        #     print("Expecting changes. ")

        self.__compare_secondary_and_continue(node_init, node_updated, indent=0)
        
        return self.result

    def __compare_secondary_and_continue(self, node_init, node_updated, indent=0):
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

        # compare children and raise dissimilarity if necessary.
        [nodes_unchanged, nodes_added, nodes_deleted] = self.utils.calc_intersection(children_init, children_updated,
                                                                                     matching_method)

        # consider the exceptional case that the EntityType has changed. Then, the relTypes are still the same but
        # chances are high that a structural change makes life a lot easier on the long run
        to_remove = []
        for n1, n2 in nodes_unchanged:
            if n1.get_entity_type() != n2.get_entity_type():
                # remove pair from unchanged list
                to_remove.append((n1, n2))
                # add n1 to nodes_removed
                nodes_deleted.append(n1)
                # add n2 to nodes_inserted
                nodes_added.append(n2)

        nodes_unchanged = [pair for pair in nodes_unchanged if pair not in to_remove]

        # check if nodes in nodes_unchanged got already matched but a previous subtree analysis
        import copy
        unchanged_pairs = copy.deepcopy(nodes_unchanged)
        for pair in unchanged_pairs:
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
            self.__compare_secondary_and_continue(matchingChildPair[0], matchingChildPair[1], indent=indent + 1)

        return

    def calc_dict_diff(self, dict_init: dict, dict_updated: dict) -> dict:
        """
        calculates the difference between two dictionaries and returns a dictionary with the differences in apoc.diff style
        @param dict_init: the initial attrs of the node 
        @param dict_updated: the updated attrs of the node
        @return: 
        """
        # Same key, different/same value
        different = {}
        inCommon = {}
        for key in dict_init.keys():
            if key in dict_updated:
                if dict_init[key] != dict_updated[key]:
                    # different value
                    different[key] = {"left": dict_init[key], "right": dict_updated[key]}
                else:
                    # same value
                    inCommon[key] = dict_init[key]
        
        # Right only
        rightOnly = {}
        for key in dict_updated.keys():
            if not key in dict_init:
                rightOnly[key] = dict_updated[key]
                
        # Left only
        leftOnly = {}
        for key in dict_init.keys():
            if not key in dict_updated:
                leftOnly[key] = dict_init[key]
        
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
        # cypher = Neo4jQueryFactory.diff_nodes(node_init.id, node_updated.id)
        # raw = self.connector.run_cypher_statement(cypher)

        raw = self.calc_dict_diff(node_init.attrs, node_updated.attrs)

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

                # if SemModification has been applied to primary node, we must construct a pattern with one virtual node
                # indicated by -1
                pattern = GraphPattern(paths=[
                    GraphPath(
                        [EdgeItem(start_node=root_init, end_node=NodeItem(-1), rel_id=-1)
                         ]
                    )
                ])

            else:
                pattern = self.__get_pattern(root_init.id, node_init.id)

            pmod_list = node_diff.create_pmod_definitions(node_init, node_updated, pattern=pattern)

            # append modifications to delta
            for pm in pmod_list:
                # Note: the modification is captured even though it might be already recognized by another path.
                # please use the unify methods in the GraphDelta class to filter detected modifications afterwards
                self.result.capture_property_mod_instance(pm)

    def __get_pattern(self, root_node_id: int, current_node_id: int) -> GraphPattern:
        """
        Returns a graph pattern between two nodes specified by their ids
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

    def check_isomorphism(self) -> bool:
        """
        check isomorphism init --> updt
        # query the pattern beneath a primary node
        """

        print("Checking for isomorphism...\n")
        cy = Neo4jQueryFactory.get_distinct_paths_from_node(self.current_prim_init.id)
        res = self.connector.run_cypher_statement(cy)

        pattern = GraphPattern.from_neo4j_response(res)

        # create cypher query out of pattern (don't skip timestamps)
        cy = pattern.to_cypher_match(define_return=True, entType_guid_only=True)

        # replace init ts with updt ts in the cypher query
        ts_init = self.current_prim_init.get_timestamps()[0]
        ts_updt = self.current_prim_updated.get_timestamps()[0]
        cy = cy.replace(ts_init, ts_updt)
        print(cy)
        # search for the specified pattern in the updated graph
        res = self.connector.run_cypher_statement(cy)

        # if the response is empty, no match could be found and isomorphism is impossible
        if len(res) == 0:
            return False
        
        # check isomorphism updt --> init
        cy = Neo4jQueryFactory.get_distinct_paths_from_node(self.current_prim_updated.id)
        res = self.connector.run_cypher_statement(cy)

        pattern = GraphPattern.from_neo4j_response(res)

        # create cypher query out of pattern (don't skip timestamps)
        cy = pattern.to_cypher_match(define_return=True, entType_guid_only=True)
        
        # replace init ts with updt ts in the cypher query
        ts_init = self.current_prim_init.get_timestamps()[0]
        ts_updt = self.current_prim_updated.get_timestamps()[0]
        cy = cy.replace(ts_updt, ts_init)
        print(cy)

        res = self.connector.run_cypher_statement(cy)

        print("Isomorphism check DONE.")

        # if the reposonse is empty, no match could be found and isomorphism is impossible
        # if both isomophism checks are true (no reponses are empty) then return True
        if len(res) == 0:
            return False
        else:
            return True
