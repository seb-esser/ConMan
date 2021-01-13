
""" packages """



""" modules """
from neo4jGraphDiff.Configurator import Configurator
from neo4jGraphDiff.Reporter import Reporter

""" script """
configPath = './neo4jGraphDiff/defaultConfig.json'
config = Configurator.from_json(configPath)

print(config.LogSettings)
print(config.DiffSettings)




# reporter = Reporter()




