
""" packages """
import enum


class MatchCriteriaEnum(enum.Enum): 
    OnGuid = 1
    OnNodeType = 2
    OnRelType = 3
    OnEntityType = 4
    OnRelTypeAndOnNodeType = 5
    OnHash = 6
    OnHashWithDiffIgnore = 7



class LoggingLevelEnum(enum.Enum):
    NONE = 1
    SIMPLE = 2
    ADVANCED = 3
    FULL = 4