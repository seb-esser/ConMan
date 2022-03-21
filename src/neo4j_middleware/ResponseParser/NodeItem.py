from neo4j_middleware.Neo4jFactory import Neo4jFactory
import re


class NodeItem:
    """
    reflects the node structure from neo4j
    """

    def __init__(self, node_id: int, rel_type: str = None, entity_type: str = None, node_type: str = None):
        """

        @type node_type: the classification of PrimaryNode, SecondaryNode or ConnectionNode
        @param node_id: node id in the graph database
        @param rel_type: rel_type of edge pointing to this node
        @param entity_type: the reflected Ifc Entity name
        """
        self.id = node_id
        self.entity_type = entity_type
        self.rel_type = rel_type
        self.attrs = None
        self.node_type = node_type

    def __repr__(self):
        return 'NodeItem: id: {} EntityType: {}'.format(self.id, self.entity_type)

    def __eq__(self, other):
        """
        implements a comparison function. matching by node id
        @param other:
        @return:
        """
        if self.id == other.id:
            return True
        else:
            return False
        # ToDo: eq comparison is not valid for cypher-based DPO

    @classmethod
    def fromNeo4jResponseWithRel(cls, raw: str) -> list:
        ret_val = []
        for inst in raw:
            node_type = inst[4][0]
            child = cls(nodeId=int(inst[0]), relType=inst[1]['rel_type'], entityType=inst[2], nodeType=node_type)
            if 'listItem' in inst[1]:
                child.rel_type = inst[1]['rel_type'] + '__listItem{}'.format(inst[1]['listItem'])
                # ToDo: consider to re-model the recursive Diff approach by incorporating edgeItems
            attrs = inst[3]
            child.attrs = attrs
            ret_val.append(child)
        return ret_val

    @classmethod
    def fromNeo4jResponseWouRel(cls, raw: str) -> list:
        ret_val = []
        for inst in raw:
            node_labels = list(inst[3])
            node_type = [x for x in node_labels if not x.startswith('ts')][0]
            child = cls(nodeId=int(inst[0]), relType=None, entityType=inst[1], nodeType=node_type)
            attrs = inst[2]
            child.attrs = attrs
            ret_val.append(child)
        return ret_val

    @classmethod
    def fromNeo4jResponse(cls, raw) -> list:
        """
        creates a List of NodeItem instances from a given neo4j response
        @param raw: neo4j response string
        @return:
        """
        ret_val = []
        for node_raw in raw:
            node_labels = list(node_raw.labels)
            node_labels[:] = [x for x in node_labels if not x.startswith('ts')]
            node = cls(nodeId=int(node_raw.id), nodeType=node_labels[0], relType=None, entityType=None)
            node.setNodeAttributes(dict(node_raw._properties))
            node.entity_type = node.attrs['EntityType']
            ret_val.append(node)

        return ret_val

    @classmethod
    def from_cypher_fragment(cls, raw):

        # regex definitions
        reg_attr_extractor = r"\{([^]]+)\}"
        reg_attr_separator = r"(.+?):(.+?),"
        reg_node_var = r"^(.+?):"
        reg_node_labels = r":([^]]+)\{"

        # information to be extracted using regex
        node_var = ""
        labels = ""
        attributes = ""

        # get variable def in current cypher query (unique to each query)
        node_var = re.findall(reg_node_var, raw)[0]

        # get node labels
        node_label_raw = re.findall(reg_node_labels, raw)
        if len(node_label_raw) != 0:
            labels = node_label_raw[0].replace(" ", "").split(":")

        # get attributes
        attributes_raw = re.findall(reg_attr_extractor, raw)
        if len(attributes_raw) != 0:
            attributes = attributes_raw[0] + ", "

        all_attributes_raw = re.findall(reg_attr_separator, attributes)

        # parse attributes
        attr_dict = {}
        for t in all_attributes_raw:
            attr_dict[t[0].replace("'", "").replace(" ", "")] = t[1]
            # ToDo: cast datatypes properly

        # init new node item
        node = cls(nodeId=0)
        node.attrs = attr_dict
        # return newly created nodeItem
        return node

    def setNodeAttributes(self, attrs):
        """
        assigns attributes to node item
        @param attrs: dict or list
        @return: nothing
        """
        if isinstance(attrs, list):
            d = attrs[0]
            self.attrs = d
        else:
            self.attrs = attrs

    def tidy_attrs(self, remove_None_values: bool = True):
        """
        removes entity_type and p21_id from attr dict
        @return:
        """
        self.attrs.pop("EntityType", None)
        self.attrs.pop("p21_id", None)
        self.attrs.pop('rel_type', None)

        if remove_None_values is True:
            # remove attrs that have a none value assigned
            cleared_dict = {}
            for key, val in self.attrs.items():
                if val != 'None':
                    cleared_dict[key] = val
                if key in ['Coordinates', 'DirectionRatios']:
                    cleared_dict[key] = eval(val)
            self.attrs = cleared_dict

    def to_cypher(self, timestamp: str = None, node_identifier: str = None, include_nodeType_label: bool = False):
        """
        returns a cypher query fragment to search for this node with semantics
        @param include_nodeType_label: set to True if NodeType should be added to the CREATE statement. False by default
        @param timestamp: specify in which model you'd like to search for the node
        @param node_identifier: the variable name in the cypher query
        @return:
        """
        if node_identifier is None:
            node_identifier = 'n'
        if timestamp is None:
            ts = ''
        else:
            ts = ':{}'.format(timestamp)

        if include_nodeType_label:
            ts += ':{}'.format(self.node_type)

        # remove p21_id attribute
        cleaned_node_attrs = self.attrs
        # cleaned_node_attrs.pop('p21_id', None)

        return '({0}{1} {2})'.format(node_identifier, ts, Neo4jFactory.formatDict(self.attrs))

