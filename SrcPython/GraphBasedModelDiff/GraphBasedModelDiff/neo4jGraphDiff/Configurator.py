
import json
import enum


class Configurator:
    """global configurator for everything related to the subgraph Diff in Neo4j"""

    def __init__(self, logSettings, diffSettings): 
        self.LogSettings = logSettings
        self.DiffSettings = diffSettings
        
    @classmethod
    def basicConfig(cls):
        
        logSettings = LoggingSettings(False, False, None, None, None)
        diffSettings = DiffSettings(None, None, None, None)

        classObj = cls(logSettings, diffSettings)
        return classObj

    @classmethod
    def from_json(cls, jsonPath): 
        """ loads the config from a specified json file and returns a Configurator instance """
        
        # ToDo: prepare everything to use this method with file-based jsons as well as HTTP request bodies

       
        with open(jsonPath) as f: 
            json_obj = json.load(f)

        # snip the json
        try:
             logSettings_json = json_obj['loggingSettings']
             diffSettings_json = json_obj['diffSettings']
        except :
            raise Exception('Staged an invalid config file. please check. ')
               
        # create class instances
        logSettings = LoggingSettings.from_json(logSettings_json)      
        diffSettings = DiffSettings.from_json(diffSettings_json)      
        
        return cls(logSettings, diffSettings)


    def exportConfigToJSON(self):
        """ writes the current config to a json """
        pass


    # dunder
    

    
class LoggingSettings:

    def __init__(self, toConsole, toFile, logFilePath, logConsoleLevel, logFileLevel): 
        self.logToConsole = toConsole
        self.logToFile = toFile
        self.logFilePath = logFilePath
        self.logConsoleLevel = logConsoleLevel
        self.logFileLevel = logFileLevel


    @classmethod
    def from_json(cls, obj):
        """ generate instance from JSON """
        bool_file = obj['logToFile']
        bool_console = obj['logToConsole']
        logPath = obj['loggingFilePath']
        levelConsole = obj['loggingLevelConsole']
        levelFile = obj['loggingLevelFile']

        return cls(bool_console, bool_file, logPath, levelConsole, levelFile)

    def ToJson(self): 
        """ write instance to JSON """ 
        raise Exception('This method is not implemented yet')


    # --- dunder ---
    def __repr__(self):
        return 'LoggingSettings: ToConsole: {} ToFile: {}'.format(self.logToConsole, self.logToFile)

    def __str__(self):
        return 'LoggingSettings: ToConsole: {} ToFile: {}'.format(self.logToConsole, self.logToFile)

class DiffSettings: 
    """ """

    def __init__(self, diffMethods, hashSettings, diffSettings, ignoreSettings): 

        # list of methods that should be applied
        self.diffMethods = diffMethods
        
        # settings for each individual DIFF method
        self.hashSettings = hashSettings
        self.diffSettings = diffSettings

        # ignore settings
        self.diffIgnoreSettings = ignoreSettings

    @classmethod
    def from_json(cls, obj):
        """ generate instance from JSON """

        diff_methods = obj['diffMethods']
        hash_config = CompareSettings.from_json(obj['hashBased_settings'])
        nodeDiff_config = CompareSettings.from_json(obj['nodeDiffBased_settings'])
        diffIgnore_config = IgnoreSettings.from_json(obj['diffIgnoreSettings'])

        return cls(diff_methods, hash_config, nodeDiff_config, diffIgnore_config )

    def ToJson(self): 
        """ write instance to JSON """ 
        raise Exception('This method is not implemented yet')

     # --- dunder ---
    def __repr__(self):
        return 'DIFF Settings: Methods: {} '.format(self.diffMethods)

    def __str__(self):
        return 'DIFF Settings: Methods: {} '.format(self.diffMethods)


class CompareSettings: 

    def __init__(self, considerRelType, considerChildNodeType): 
        self.considerRelType = considerRelType
        self.considerChildNodeType = considerChildNodeType

    @classmethod
    def from_json(cls, obj): 

        relType = obj['compareSettings']['considerRelType']
        childType = obj['compareSettings']['considerChildNodeType']

        return cls(relType, childType)

class IgnoreSettings: 

    # default constructor
	def __init__(self, ignoreAttrs, ignoreNodeTypes):
		self.ignore_attrs = ignoreAttrs
		self.ignore_node_tpes = ignoreNodeTypes

	# from json factory
	@classmethod
	def from_json(cls, json_obj): 

		ignore_labels = json_obj["IgnoreNodeTypes"]
		ignore_attrs = json_obj["IgnoreNodeAttributes"]

		labels_list = []
		for ignore_label in ignore_labels: 
			labels_list.append(ignore_label)

		attrs_list = []
		for ignore_attr in ignore_attrs: 
			attrs_list.append(ignore_attr)

		return cls(attrs_list, labels_list)

class MatchCriteriaEnum(enum.Enum): 
    OnGuid = 1
    OnNodeType = 2
    OnRelType = 3
    OnEntityType = 4
    OnRelTypeAndOnNodeType = 5
    OnHash = 6
    OnHashWithDiffIgnore = 7

