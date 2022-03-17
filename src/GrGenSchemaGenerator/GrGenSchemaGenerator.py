import re

import ifcopenshell
from ifcopenshell.ifcopenshell_wrapper import enumeration_type


class GrGenSchemaGenerator:

    def __init__(self):
        self.gm_content: str = ""
        self.enumerations = []
        self.type_mapping = {
            "string": "string",
            "real": "double",
            "integer": "int",
            "logical": "boolean",
            "binary": "string",
            "boolean": "boolean"
        }

    def generate_gm_file(self):
        """
        generates a gm Graph Model file for usage within the GrGen system
        @return:
        """

        self.gm_content += self.create_file_header() + '\n\n'

        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4")
        entities = ifcopenshell.ifcopenshell_wrapper.schema_definition.entities(schema)
        # enums = ifcopenshell.ifcopenshell_wrapper.schema_definition.enumeration_types(schema)
        # selects = ifcopenshell.ifcopenshell_wrapper.schema_definition.select_types(schema)

        # encodings of entities
        for e in entities:

            entity_name = e.name()
            is_abstract = e.is_abstract()
            supertype = e.supertype()
            node_attrs, single_associations, aggregated_associations, enums = self.separate_attributes(e)
            # node_attrs = e.all_attributes()
            gm_snippet: str = ""
            if is_abstract:
                gm_snippet += "abstract "

            # write class skeleton
            gm_snippet += """node class {0} """.format(entity_name)

            # handle extends case
            if supertype is not None:
                gm_snippet += "extends {} {{".format(supertype.name())
            else:
                gm_snippet += "{"
            # write attributes
            for attr in node_attrs:
                attr_name = attr.name()
                idx = e.attribute_index(attr_name)
                data_type = e.attribute_by_index(idx).type_of_attribute()

                # process datatype:
                s = str(data_type)
                # print(s)
                splitt: str = s.split('<')[-1]
                ty = splitt.translate({ord(i): None for i in ['<', '>']})

                try:
                    grgen_type = self.type_mapping[ty]
                except:
                    print(Warning("Skipped parsing of attribute {} of primary_node_type {}.". format(attr_name, entity_name)))

                    continue
                    # raise Exception("the detected datatype has no mapping rule in the dictionary. ")
                # attributes with simple types
                try:
                    gm_snippet += "\n\t{}: {};".format(attr_name, grgen_type)
                except:
                    print("something was skipped. Please check primary_node_type {} attribute {}".format(entity_name, attr_name))
                    continue
            # close class skeleton
            gm_snippet += " \n}"
            self.gm_content += gm_snippet + "\n\n"

        processed_names = []
        for en in self.enumerations:
            ty = str(en.type_of_attribute())
            # format string representation
            split = ty.split(' ')
            entity_name = split[1][:-1]
            if entity_name in processed_names:
                # enum was already processed, proceed with next one
                continue
            enum_values = split[2:]

            enum_values[0] = enum_values[0][1:]
            enum_values[-1] = enum_values[-1][:-2]
            inner = ""
            for values in enum_values:
                inner += (values + " ")
            self.gm_content += "enum {0} {{ {1} }}\n".format(entity_name, inner)
            processed_names.append(entity_name)

        return self.gm_content

# ToDo: the following method was copied from Ifc2GraphTranslator.py.
#  Consider to introduce a global utility module that provides both classes a suitable implementation
    def separate_attributes(self, entity) -> tuple:
        """"
        Queries all attributes of the corresponding primary_node_type definition and returns if an attribute has
        attr type value, an primary_node_type value or is an aggregation of entities
        @primary_node_type:
        @return:
        """
        name = entity.name()
        class_definition = entity.attributes()

        # separate attributes into node attributes, simple associations, and sets of associations
        node_attributes = []
        single_associations = []
        aggregated_associations = []
        enums = []

        for attr in class_definition:
            try:
                attr_type = attr.type_of_attribute().declared_type()
            except:
                attr_type = attr.type_of_attribute()

            # get the value structure
            is_entity = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.entity)
            is_type = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.type_declaration)
            is_select = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.select_type)

            is_pdt_select = False
            is_entity_select = False
            is_nested_select = False

            # ToDo: Distinguish if it is a select of entities or a select of predefinedTypes
            if is_select:
                lst = attr.type_of_attribute().declared_type().select_list()

                is_entity_select = all(
                    [isinstance(x, ifcopenshell.ifcopenshell_wrapper.entity) for x in lst])
                is_pdt_select = all(
                    [isinstance(x, ifcopenshell.ifcopenshell_wrapper.type_declaration) for x in lst])
                is_nested_select = all(
                    [isinstance(x, ifcopenshell.ifcopenshell_wrapper.select_type) for x in lst])
                # ToDo: mixed cases are not implemented yet:
                # - select + entities
                # - select + type declaration (RelatingPropertyDefinition
                # 'Roles' in IfcActor
                if not all([is_entity_select, is_pdt_select, is_nested_select]):
                    continue

            is_enumeration = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.enumeration_type)
            is_aggregation = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.aggregation_type)

            # catch some weird cases with IfcDimensionalExponents
            #  as this primary_node_type doesnt use types but atomic attr declarations
            if attr.name() in ['LengthExponent',
                               'MassExponent',
                               'TimeExponent',
                               'ElectricCurrentExponent',
                               'ThermodynamicTemperatureExponent',
                               'AmountOfSubstanceExponent',
                               'LuminousIntensityExponent',
                               'Exponent',  # from IfcDerivedUnitElement
                               'Precision',  # from IfcGeometricRepresentationContext
                               'Scale',  # from IfcCartesianPointTransformationOperator3D in 2x3
                               #'Orientation',  # from IfcFaceOuterBound in 2x3
                               'SelfIntersect',  # from IfcCompositeCurve in 2x3
                               'SameSense',  # from IfcCompositeCurveSegment in IFC2x3
                               'SenseAgreement',  # from IfcTrimmedCurve in IFC2x3
                               'AgreementFlag',  # from IfcPolygonalBoundedHalfSpace
                               'ParameterTakesPrecedence',
                               'ClosedCurve',
                               'SelfIntersect',
                               'LayerOn',
                               'LayerFrozen',
                               'LayerBlocked',
                               'ProductDefinitional',
                               'Scale2',  # IfcCartesianTransformationOperator2DnonUniform
                               'Scale3',
                               'RelatedPriorities',
                               'RelatingPriorities',
                               'SameSense',
                               'AgreementFlag',
                               'USense',
                               'VSense',
                               'WeightsData',
                               'Weights',
                               'Sizeable',
                               'ParameterTakesPrecedence',
                               'IsCritical',
                               'DestabilizingLoad',
                               'IsLinear',
                               'RepeatS',
                               'RepeatT',
                               'IsHeading',
                               'IsMilestone',
                               'Priority',
                               'SenseAgreement',
                               'IsPotable',
                               'NumberOfRiser',
                               'NumberOfTreads',
                               'Pixel',
                               'InputPhase',
                               'Degree',
                               'ImpliedOrder', # IfcRelInterferesElements -> attr
                               'RefLongitude',
                               'RefLatitude',
                               'RemainingUsage',
                               'Completion',
                               'ActualUsage',
                               'ScheduleUsage',
                               'RelatingPriorities',
                               'RelatedPriorities'
                               ]:
                node_attributes.append(attr)
            elif is_enumeration:
                # assign to local return value
                enums.append(attr)

                if attr not in self.enumerations:
                    self.enumerations.append(attr)
                # continue with next attribute
                continue

            elif is_type or is_pdt_select or is_nested_select:
                node_attributes.append(attr)
                continue
            elif is_entity or is_entity_select:
                single_associations.append(attr)
                continue
            elif is_aggregation:
                # ToDo: check if it is an aggregation of types or an aggregation of entities
                # https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/link/ifctrimmedcurve.htm -> trimSelect
                if attr.name() in [
                    'Coordinates',
                    'DirectionRatios',
                    'CoordList',
                    'segments',
                    'MiddleNames',
                    'PrefixTitles',
                    'SuffixTitles',

                    'Addresses',
                    'CoordIndex',
                    'InnerCoordIndices',
                    'Trim1',
                    'Trim2',
                    'Orientation',
                    'RefLongitude',
                    'RefLatitude',
                    'Transparency' # IfcSurfaceStyleShading
                ]:
                    node_attributes.append(attr)
                else:
                    aggregated_associations.append(attr)
            else:
                raise Exception('Failed to encode the attribute type of primary_node_type {} attribute {}. '
                                'Please check your graph translator.'.format(name, attr))
        # node_attributes.append('id')
        # node_attributes.append('type')
        return node_attributes, single_associations, aggregated_associations, enums

    def create_file_header(self):
        """
        Specifies a file header for gm text files
        @return:
        """
        s = """// ---------- TUM CMS - 2021 ---------- 
// gm file to be used within GrGen 
// sebastian.esser[at]tum.de
// 
// ____________________________________
        """
        return s



