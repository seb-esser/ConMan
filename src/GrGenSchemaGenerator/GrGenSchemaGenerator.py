import ifcopenshell


class GrGenSchemaGenerator:

    def __init__(self):
        self.gm_content: str = ""

    def generate_gm_file(self):
        """
        generates a gm Graph Model file for usage within the GrGen system
        @return:
        """

        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4")
        entities = ifcopenshell.ifcopenshell_wrapper.schema_definition.entities(schema)
        for e in entities:
            name = e.name()
            is_abstract = e.is_abstract()
            supertype = e.supertype()
            node_attrs, single_associations, aggregated_associations = self.separate_attributes(e)

            gm_snippet: str = """node class {0} {{ }}""".format(name)
            self.gm_content += gm_snippet + "\n"
        print(self.gm_content)
        return self.gm_content

# ToDo: the following method was copied from Ifc2GraphTranslator.py.
#  Consider to introduce a global utility module that provides both classes a suitable implementation
    def separate_attributes(self, entity) -> tuple:
        """"
        Queries all attributes of the corresponding entity definition and returns if an attribute has
        attr type value, an entity value or is an aggregation of entities
        @entity:
        @return:
        """
        name = entity.name()
        class_definition = entity.all_attributes()

        # info = entity.get_info()
        # clsName = info['type']
        # entity_id = info['id']
        #
        # # remove entity_id and type
        # # info.pop('id')
        # # info.pop('type')
        #
        # # get the class definition for the current instance w.r.t. schema version
        # # https://wiki.osarch.org/index.php?title=IfcOpenShell_code_examples#Exploring_IFC_schema
        #
        # separate attributes into node attributes, simple associations, and sets of associations
        node_attributes = []
        single_associations = []
        aggregated_associations = []
        #
        # try:
        #     class_definition = self.schema.declaration_by_name(
        #         clsName).all_attributes()
        # except:
        #     raise Exception("Failed to query schema specification in IFC2GraphTranslator.\n "
        #                     "Schema: {}, Entity: {} ".format(self.schema, clsName))

        for attr in class_definition:
            # check if attribute has attr value in the current entity instance
            # if info[name] is not None:
            #     print('attribute present')
            # else:
            #     print('attribute empty')
            #     continue

            # this is attr quite weird approach but it works
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
                # methods = attr.type_of_attribute().declared_type()
                # print(dir(methods))

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
                if not all([is_entity_select, is_pdt_select, is_nested_select]):
                    continue

            is_enumeration = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.enumeration_type)
            is_aggregation = isinstance(
                attr_type, ifcopenshell.ifcopenshell_wrapper.aggregation_type)

            # catch some weird cases with IfcDimensionalExponents
            #  as this entity doesnt use types but atomic attr declarations
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
                               'Orientation',  # from IfcFaceOuterBound in 2x3
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
                               'ImpliedOrder' # IfcRelInterferesElements -> attr
                               ]:
                node_attributes.append(attr.name())

            elif is_type or is_enumeration or is_pdt_select or is_nested_select:
                node_attributes.append(attr.name())
            elif is_entity or is_entity_select:
                single_associations.append(attr.name())
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
                    'Roles',
                    'Addresses',
                    'CoordIndex',
                    'InnerCoordIndices',
                    'Trim1',
                    'Trim2',
                    'Orientation',
                    'RefLongitude',
                    'RefLatitude'
                ]:
                    node_attributes.append(attr.name())
                else:
                    aggregated_associations.append(attr.name())
            else:
                raise Exception('Failed to encode the attribute type of entity {} attribute {}. '
                                'Please check your graph translator.'.format(name, attr.name()))
        node_attributes.append('id')
        node_attributes.append('type')
        return node_attributes, single_associations, aggregated_associations





