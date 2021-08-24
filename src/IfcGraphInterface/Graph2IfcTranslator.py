""" File content copy-pasted from: http://academy.ifcopenshell.org/creating-a-simple-wall-with-property-set-and-quantity-information/ """

import uuid
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
import ifcopenshell

from neo4j_middleware.neo4jConnector import Neo4jConnector


class Graph2IfcTranslator:
    """

    """

    def __init__(self, connector: Neo4jConnector, ts: str, schema_identifier: str = 'IFC4'):
        """

        @param connector:
        @param ts:
        """
        self.model = ifcopenshell.file(schema=schema_identifier)
        self.node_id_2_spf_id = {}
        self.connector = connector
        self.ts = ts

    def get_model(self):
        """
        returns the current model object
        @return ifcopenshell model object
        """
        return self.model

    def build_entity(self, graph_node_id: int, class_name: str, attributes: dict):
        """
        builds an entity and adds it into the ifc model
        @param graph_node_id:
        @param class_name:
        @param attributes:
        @return: the SPF ID
        """

        try:
            print('building entity {}'.format(class_name))

            # for key, val in attributes.items():
            #     if key in [
            #         'Coordinates',
            #         'DirectionRatios',
            #         'CoordList',
            #         'segments',
            #         'MiddleNames',
            #         'PrefixTitles',
            #         'SuffixTitles',
            #         'Roles',
            #         'Addresses',
            #         'CoordIndex',
            #         'InnerCoordIndices',
            #         'Trim1',
            #         'Trim2',
            #         'Orientation',
            #         'RefLongitude']:
            #         print(val)

            e = self.model.create_entity(class_name, **attributes)

            # save node id 2 spf id in dict
            self.node_id_2_spf_id[graph_node_id] = e.id()

            return e.id()
        except:
            print('class: {}'.format(class_name))
            print('attrs: {}'.format(attributes))
            raise Exception("Error in creating ifc entity. ")

    def build_association(self, parent_node_id: int, child_node_id: int, association_name: str):
        """
        creates an association among two IFC entities specified by an directed edge in the graph representation
        @param parent_node_id:
        @param child_node_id:
        @param association_name:
        @return:
        """
        spf_id_parent = self.node_id_2_spf_id[parent_node_id]
        spf_id_child = self.node_id_2_spf_id[child_node_id]

        parent = self.model.by_id(spf_id_parent)
        child = self.model.by_id(spf_id_child)

        # test if the desired association is modeled as a pointer or an array of pointers
        if not association_name.find("listItem") == -1:
            name = association_name.split('__')[0]
            # list of pointers
            try:
                lst = getattr(parent, name)
                if lst is None:
                    lst = []
                elif type(lst) is tuple:
                    lst = list(lst)

                if child not in lst:
                    lst.append(child)
                    setattr(parent, name, lst)
            except:
                print('Skip building {} between #{} and #{}'.format(association_name, spf_id_parent, spf_id_child))
        else:
            try:
                setattr(parent, association_name, child)
            except:
                print('Skip building {} between #{} and #{}'.format(association_name, spf_id_parent, spf_id_child))

    def build_childs(self, n, rec):
        """
        queries all direct child nodes to node n and inserts their semantics into the IFC SPF model
        @param n:
        @param rec: triggers if this method should be carried out recursively
        @return:
        """
        # build association
        query_factory = Neo4jQueryFactory()
        cy = query_factory.get_child_nodes(self.ts, n.id)
        raw_res = self.connector.run_cypher_statement(cy)

        # cast cypher response in a list of node items
        child_nodes = NodeItem.fromNeo4jResponseWithRel(raw_res)

        # check if leaf node was found
        if len(child_nodes) == 0:
            return

        for c in child_nodes:
            # query all node properties of n
            cy = query_factory.get_node_properties_by_id(c.id)
            raw_res = self.connector.run_cypher_statement(cy, "properties(n)")

            # assign properties to node object
            c.setNodeAttributes(raw_res)

            c.tidy_attrs()

            # check if IFC counterpart to current node was already initialized
            spf_id = self.lookup_ifc_counterpart_exists(c.id)
            if spf_id == -1:
                # build IFC entity
                self.build_entity(c.id, c.entityType, c.attrs)

            # build association
            self.build_association(n.id, c.id, c.relType)

            if rec:
                self.build_childs(c, True)

    def lookup_ifc_counterpart_exists(self, node_id) -> int:
        """
        checks if an ifc entity already exists in the model, which models the current graph node
        @param node_id: the graph node
        @return: -1 if entity doesnt exist, spf_id otherwise
        """
        if node_id in self.node_id_2_spf_id:
            return self.node_id_2_spf_id[node_id]
        else:
            return -1

    def save_model(self, path) -> bool:
        """
        writes the IFC model into a file
        @param path: file path where the IFC model should be saved
        @return:
        """
        try:
            self.model.write(path + ".ifc")
            return True
        except:
            return False

    def generateSPF(self):
        """
        translates a graph from neo4j into an IFC SPF file
        @return:
        """

        # get all primary nodes
        cy = Neo4jQueryFactory.get_primary_nodes(self.ts)
        raw_res = self.connector.run_cypher_statement(cy)

        # cast cypher response in a list of node items
        nodes = NodeItem.fromNeo4jResponseWouRel(raw_res)

        print('---- Building primary & secondary nodes. ----')
        for n in nodes:
            # query all node properties of n
            cy = Neo4jQueryFactory.get_node_properties_by_id(n.id)
            raw_res = self.connector.run_cypher_statement(cy, "properties(n)")
            # assign properties to node object
            n.setNodeAttributes(raw_res)

            n.tidy_attrs()

            # build IFC entity
            self.build_entity(n.id, n.entityType, n.attrs)

            self.build_childs(n, True)

        print('---- Primary & secondary nodes done. ----')

        # get all connection nodes
        cn = Neo4jQueryFactory.get_connection_nodes(self.ts)
        raw_res = self.connector.run_cypher_statement(cn)

        connection_nodes = NodeItem.fromNeo4jResponseWouRel(raw_res)

        print('---- Building connection nodes. ----')
        for cnode in connection_nodes:
            cy = Neo4jQueryFactory.get_node_properties_by_id(cnode.id)
            raw_res = self.connector.run_cypher_statement(cy, "properties(n)")
            # assign properties to node object
            cnode.setNodeAttributes(raw_res)

            cnode.tidy_attrs()

            # build IFC entity
            self.build_entity(cnode.id, cnode.entityType, cnode.attrs)

            # build the childs (non-recursive)
            self.build_childs(cnode, False)

        print('---- Connection Nodes done. ----')
