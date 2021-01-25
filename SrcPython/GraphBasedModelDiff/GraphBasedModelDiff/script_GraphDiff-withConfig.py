
""" packages """



""" modules """
from neo4jGraphDiff.Configurator import Configurator
from neo4jGraphDiff.Reporter import Reporter

""" script """


config = Configurator.basicConfig()

print(config.LogSettings)
print(config.DiffSettings)




# reporter = Reporter()




