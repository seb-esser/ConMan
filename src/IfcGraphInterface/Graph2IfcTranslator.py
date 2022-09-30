""" File content copy-pasted from: http://academy.ifcopenshell.org/creating-a-simple-wall-with-property-set-and-quantity-information/ """
import ast
import uuid
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
import ifcopenshell
import progressbar

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
        builds an primary_node_type and adds it into the ifc model
        @param graph_node_id:
        @param class_name:
        @param attributes:
        @return: the SPF ID
        """

        try:
            # print('building primary_node_type {}'.format(class_name))

            for key, val in attributes.items():
                if key in [
                    # 'Coordinates',
                    # 'DirectionRatios',
                    'CoordList',
                    'segments',
                    #         'MiddleNames',
                    #         'PrefixTitles',
                    #         'SuffixTitles',
                    #         'Roles',
                    #         'Addresses',
                    'CoordIndex',
                    'InnerCoordIndices',
                    'Trim1',
                    'Trim2',
                    #         'Orientation',
                    'RefLongitude',
                    'RefLatitude'
                ]:
                    attributes[key] = ast.literal_eval(val)
                    # https://stackoverflow.com/questions/24004241/convert-string-to-nested-tuple-python

                elif key in ['ValueComponent']:
                    splitted = val.split('(')
                    # extract the name
                    nested_entity_name = splitted[0]
                    # extract the value and cast to float datatype
                    nested_val = float(splitted[1][:-1])
                    nested_entity = self.model.create_entity(nested_entity_name, nested_val)
                    attributes[key] = nested_entity

                elif key in ['NominalValue']:
                    splitted = val.split('(')
                    # extract the name
                    nested_entity_name = splitted[0]
                    # extract the value and cast to float datatype
                    nested_val = splitted[1][:-1]
                    nested_entity = self.model.create_entity(nested_entity_name, nested_val)
                    attributes[key] = nested_entity

                    # todo
                    # https://academy.ifcopenshell.org/posts/using-the-parsing-functionality-of-ifcopenshell-interactively/

            del attributes['EntityType']
            e = self.model.create_entity(class_name, **attributes)

            # save node id 2 spf id in dict
            self.node_id_2_spf_id[graph_node_id] = e.id()

            return e.id()
        except:
            raise Exception("Error in creating instance of {} with attributes {} ".format(class_name, attributes))

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
        if 'listItem' in association_name:
            name = association_name['rel_type']
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
                setattr(parent, association_name['rel_type'], child)
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
        child_nodes = []

        for pair in raw_res:
            child_node_raw = pair[0]
            edge_raw = pair[1]
            child_node = NodeItem.from_neo4j_response(child_node_raw)[0]

            # add relationship data to node
            child_node.rel_type = edge_raw
            # ToDo: Hier überprüfen, ob die Daten entsprechend der Erwartungen auf das rel_type Attribut geschrieben werden

            child_nodes.append(child_node)
        # check if leaf node was found
        if len(child_nodes) == 0:
            return

        # for some geometries, the order of instantiation is important. Therefore, we sort the nodes here w.r.t listItem
        # sorted_child_nodes = sorted(child_nodes, key=lambda cnode: cnode.get_listitem())
        sorted_child_nodes = child_nodes

        print([x.get_listitem() for x in sorted_child_nodes])

        for c in sorted_child_nodes:
            c.tidy_attrs()

            # check if IFC counterpart to current node was already initialized
            spf_id = self.lookup_ifc_counterpart_exists(c.id)
            if spf_id == -1:
                # build IFC primary_node_type
                self.build_entity(c.id, c.get_entity_type(), c.attrs)

            # build association
            self.build_association(n.id, c.id, c.rel_type)

            if rec:
                self.build_childs(c, True)

    def lookup_ifc_counterpart_exists(self, node_id) -> int:
        """
        checks if an ifc primary_node_type already exists in the model, which models the current graph node
        @param node_id: the graph node
        @return: -1 if primary_node_type doesnt exist, spf_id otherwise
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
            self.model.write(path)
            return True
        except:
            return False

    def generate_SPF(self):
        """
        translates a graph from neo4j into an IFC SPF file
        @return:
        """

        # get all primary nodes
        cy = Neo4jQueryFactory.get_primary_nodes(self.ts)
        raw_res_pr = self.connector.run_cypher_statement(cy)

        # get all connection nodes
        cn = Neo4jQueryFactory.get_connection_nodes(self.ts)
        raw_res_cn = self.connector.run_cypher_statement(cn)

        # cast cypher response in a list of primary/connection node items
        nodes_pr = NodeItem.from_neo4j_response(raw_res_pr)
        nodes_cn = NodeItem.from_neo4j_response(raw_res_cn)

        increment = 100 / (len(nodes_pr) + len(nodes_cn))
        percent = 0

        for n in nodes_pr:
            # print progressbar
            progressbar.print_bar(percent)
            
            n.tidy_attrs()

            # build IFC primary_node_type
            self.build_entity(n.id, n.get_entity_type(), n.attrs)
            self.build_childs(n, rec=True)

            percent += increment

        
        for cnode in nodes_cn:
            # print progressbar
            progressbar.print_bar(percent)

            cnode.tidy_attrs()

            # build IFC primary_node_type
            self.build_entity(cnode.id, cnode.get_entity_type(), cnode.attrs)

            # build the childs (non-recursive)
            self.build_childs(cnode, False)

            percent += increment

        progressbar.print_bar(percent)
        print('[Graph:{} >> IFC_P21]: Generating file - DONE.\n'.format(self.ts))

