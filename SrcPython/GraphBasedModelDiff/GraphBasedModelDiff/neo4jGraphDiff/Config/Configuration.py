""" packages """
import json

""" modules """
from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum, LoggingLevelEnum


class Configuration:
    """global configurator for everything related to the subgraph Diff in Neo4j"""

    def __init__(self, log_settings, diff_settings):
        """
        Constructor
        @param log_settings:
        @param diff_settings:
        """
        self.LogSettings = log_settings
        self.DiffSettings = diff_settings

    @classmethod
    def basic_config(cls):
        """
        Creates a default configuration without printing to console.
        @return: Config instance
        """
        logSettings = LoggingSettings.default_settings()
        diffSettings = DiffSettings()

        classObj = cls(logSettings, diffSettings)
        return classObj

    @classmethod
    def rel_type_config(cls):
        """
        Creates a default configuration without printing to console.
        @return: Config instance
        """
        logSettings = LoggingSettings.default_settings()
        diffSettings = DiffSettings()
        diffSettings.MatchingType_Childs = MatchCriteriaEnum.OnRelType

        classObj = cls(logSettings, diffSettings)
        return classObj

    @classmethod
    def entity_type_config(cls):
        """
        
        @return: Config instance
        """
        logSettings = LoggingSettings.default_settings()
        diffSettings = DiffSettings()
        diffSettings.MatchingType_Childs = MatchCriteriaEnum.OnEntityType

        classObj = cls(logSettings, diffSettings)
        return classObj

    @classmethod
    def on_guid_config(cls):
        """
        
        @return: Configuration
        """
        logSettings = LoggingSettings.default_settings()
        diffSettings = DiffSettings()
        diffSettings.MatchingType_RootedNodes = MatchCriteriaEnum.OnGuid
        diffSettings.MatchingType_Childs = MatchCriteriaEnum.OnRelType

        classObj = cls(logSettings, diffSettings)
        return classObj

    @classmethod
    def from_json(cls, jsonPath):
        """ loads the config from a specified json file and returns a Configuration instance """

        raise Warning('not implemented properly. Check ToDos')

        # ToDo: prepare everything to use this method with file-based jsons as well as HTTP request bodies

        with open(jsonPath) as f:
            json_obj = json.load(f)

        # snip the json
        try:
            logSettings_json = json_obj['loggingSettings']
            diffSettings_json = json_obj['diffSettings']
        except:
            raise Exception('Staged an invalid config file. please check. ')

        ## create class instances
        # logSettings = LoggingSettings.from_json(logSettings_json)
        # diffSettings = DiffSettings.from_json(diffSettings_json)

        return cls(logSettings, diffSettings)

    def to_json(self):
        """ writes the current config to a json """
        pass

    # dunder
    def __repr__(self):
        return 'Config: matchingType_rootedNodes: {} matchingType_components: {}'.format(
            self.DiffSettings.MatchingType_RootedNodes, self.DiffSettings.MatchingType_Childs)


class LoggingSettings:
    def __init__(self, to_console, to_file, log_file_path, log_console_level, log_file_level):
        self.logToConsole = to_console
        self.logToFile = to_file
        self.logFilePath = log_file_path
        self.logConsoleLevel = log_console_level
        self.logFileLevel = log_file_level

    @classmethod
    def default_settings(cls):
        return cls(False, False, '/logging', LoggingLevelEnum.NONE, LoggingLevelEnum.NONE)

    @classmethod
    def from_json(cls, obj):
        """ generate instance from JSON """
        bool_file = obj['logToFile']
        bool_console = obj['logToConsole']
        logPath = obj['loggingFilePath']
        levelConsole = obj['loggingLevelConsole']  # ToDo: Implement cast to LoggingLevelEnum
        levelFile = obj['loggingLevelFile']  # ToDo: Implement cast to LoggingLevelEnum

        return cls(bool_console, bool_file, logPath, levelConsole, levelFile)

    def to_json(self):
        """ write instance to JSON """
        raise Exception('This method is not implemented yet')

    # --- dunder ---
    def __repr__(self):
        return 'LoggingSettings: ToConsole: {} ToFile: {}'.format(self.logToConsole, self.logToFile)

    def __str__(self):
        return 'LoggingSettings: ToConsole: {} ToFile: {}'.format(self.logToConsole, self.logToFile)


class DiffSettings:
    """ """

    def __init__(self):
        # ignore settings
        self.diffIgnoreAttrs = ["p21_id", "GlobalId"]
        self.diffIgnoreEntityTypes = ["IfcOwnerHistory"]
        self.MatchingType_RootedNodes = MatchCriteriaEnum.OnHash  # sets how rooted nodes get matched
        self.MatchingType_Childs = MatchCriteriaEnum.OnHash  # sets how child nodes get matched

    @classmethod
    def defaultSettings(cls):
        return cls()

    @classmethod
    def from_json(cls, obj):
        """ generate instance from JSON """
        raise Exception('This method is not implemented yet')

    def ToJson(self):
        """ write instance to JSON """
        raise Exception('This method is not implemented yet')

    # --- dunder ---
    def __repr__(self):
        return 'DiffSettings: IgnoreAttrs: {} IgnoreEntityTypes: {}'.format(self.diffIgnoreAttrs,
                                                                            self.diffIgnoreEntityTypes)

    def __str__(self):
        return 'DiffSettings: IgnoreAttrs: {} IgnoreEntityTypes: {}'.format(self.diffIgnoreAttrs,
                                                                            self.diffIgnoreEntityTypes)