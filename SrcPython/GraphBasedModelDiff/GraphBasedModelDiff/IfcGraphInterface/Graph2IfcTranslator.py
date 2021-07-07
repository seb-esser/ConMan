""" File content copy-pasted from: http://academy.ifcopenshell.org/creating-a-simple-wall-with-property-set-and-quantity-information/ """

import uuid
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
import ifcopenshell

create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)


class Graph2IfcTranslator:
    """

    """

    def __init__(self):

        self.model = ifcopenshell.file(schema='IFC4')
        self.node_id_2_spf_id = {}
        pass

    def get_model(self):
        """
        returns the current model object
        @return ifcopenshell model object
        """
        return self.model

    def build_entity(self, graph_node_id: int, class_name: str, attributes: dict):
        """
        builds an entity and adds it into the ifc model
        @param class_name:
        @param attributes:
        @return: the SPF ID
        """



        try:
            print('building entity {}'.format(class_name))
            e = self.model.create_entity(class_name, **attributes)

            # save node id 2 spf id in dict
            self.node_id_2_spf_id[graph_node_id] = e.id()

            return e.id()
        except:
            print('class: {}'.format(class_name))
            print('attrs: {}'.format(attributes))
            raise Exception("Error in creating ifc entity. ")

    def build_association(self, parent_node_id: int, child_node_id: int, association_name: str):
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
                lst.append(child)
                setattr(parent, name, lst)
            except:
                print('Skip building {} between #{} and #{}'.format(association_name, spf_id_parent, spf_id_child))
        else:
            try:
                setattr(parent, association_name, child)
            except:
                print('Skip building {} between #{} and #{}'.format(association_name, spf_id_parent, spf_id_child))

    def build_childs(self, n, rec, connector, ts):
    # build association
        query_factory = Neo4jQueryFactory()
        cy = query_factory.get_child_nodes(ts, n.id)
        raw_res = connector.run_cypher_statement(cy)

        # cast cypher response in a list of node items
        childs = NodeItem.fromNeo4jResponseWithRel(raw_res)
        if len(childs) == 0:
            return

        for c in childs:
            # query all node properties of n
            cy = query_factory.get_node_properties_by_id(c.id)
            raw_res = connector.run_cypher_statement(cy, "properties(n)")
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
                self.build_childs(c, True, connector, ts)

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
