
import enum


class OperationsEnums(enum):
    # node add/delete
    AddNode = 1
    DeleteNode = 2

    # node modifications
    AddAttribute = 3
    DeleteAttribute = 4
    ModifyAttribute = 5

    # edge operations
    AddRelationship = 10
    DeleteRelationship = 11

    # tests verifying integrity
    TestNodeExists = 6
    TestRelationshipExists = 7
    TestAttributeExists = 8 # can be on node or rel


