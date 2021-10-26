from GrGenSchemaGenerator.GrGenSchemaGenerator import GrGenSchemaGenerator

generator = GrGenSchemaGenerator()

gm = generator.generate_gm_file()

with open("IFC4_graphModel.gm", "w") as f:
    f.write(gm)

