# This is a test script to showcase:
# 1. load two IFC models
# 2. diff models
# 3. formulate patch

# 5. apply patch

# 6. create IFC model out of the updated graph
from IfcGraphInterface.Ifc2GraphTranslator import IFCGraphGenerator
from PatchManager.Patch import Patch
from neo4jGraphDiff.GraphDiff import GraphDiff

from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

model_name_init = './00_sampleData/IFC_stepP21/GeomRepresentation_05/cube_single.ifc'
model_name_updated = './00_sampleData/IFC_stepP21/GeomRepresentation_05/cube_double.ifc'

label_init = 'ts20210623T091748'
label_updated = 'ts20210623T091749'

skip_part_1 = False
print_diff_report = False

connector.run_cypher_statement('MATCH (n) DETACH DELETE n')

# 1 -- load models into graph --
if not skip_part_1:

    print('STEP 1: Generate graph initial and graph updated... ')
    graphGenerator_init = IFCGraphGenerator(connector, model_name_init, None)
    graphGenerator_init.generateGraph()

    graphGenerator_updated = IFCGraphGenerator(connector, model_name_updated, None)
    graphGenerator_updated.generateGraph()
    print('Graphs generated successfully')

# 2 -- diff models --
diff = GraphDiff(connector=connector, ts_init=label_init, ts_updated=label_updated)
report = diff.run_diff(connector=connector)
if print_diff_report:
    report.print_report()

# 3 -- generate patch --
patch_generator = PatchGenerator(connector=connector)
patch = patch_generator.create_patch_from_graph_diff(report)

f = patch.to_json()
print(f)

print(patch.operations[0].pattern.to_cypher_query_indexed())
print(patch.operations[0].pattern.to_cypher_merge())
# 4 -- receive and apply patch on a specified graph
incoming_patch: Patch = patch

print('DEBUG INFO: initial model gets re-created with timestamp: 9999')

graphGenerator_artificial = IFCGraphGenerator(connector, model_name_init, None)
graphGenerator_artificial.label = 'ts9999'
label_toBeUpdated = graphGenerator_artificial.generateGraph()

print(patch.operations[0].pattern.to_cypher_merge(timestamp=label_toBeUpdated))
exit()

integrator = PatchIntegrator(connector=connector)
# integrator.apply_patch(incoming_patch)

# finally, disconnect from database
connector.disconnect_driver()
