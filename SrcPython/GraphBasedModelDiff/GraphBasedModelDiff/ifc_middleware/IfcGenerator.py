""" File content copy-pasted from: http://academy.ifcopenshell.org/creating-a-simple-wall-with-property-set-and-quantity-information/ """

import uuid
import time
import tempfile
import ifcopenshell

create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)


class IfcGenerator:

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
            e = self.model.create_entity(class_name, **attributes)

            # save node id 2 spf id in dict
            self.node_id_2_spf_id[graph_node_id] = e.id()

            return e.id()
        except:
            raise Exception("Error in creating ifc entity. ")

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
