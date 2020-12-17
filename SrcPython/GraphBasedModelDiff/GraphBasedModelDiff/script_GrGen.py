
from grGen_middleware.ifcGrGen_SchemaMapper import IfcGrGen_SchemaMapper as grGenSchema

grGen = grGenSchema()

grGen.load_schema_from_url('https://standards.buildingsmart.org/IFC/DEV/IFC4_3/RC2/EXPRESS/IFC4x3_RC2.exp')
#grGen.print_schema()

grGen.split_global_tokens()






