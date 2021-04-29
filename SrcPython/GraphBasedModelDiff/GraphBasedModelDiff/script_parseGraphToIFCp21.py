

from ifc_middleware.IfcGenerator import IfcGenerator


generator = IfcGenerator()
model = generator.build_file_skeleton()

rooted_elems = model.by_type('IfcRoot')

for r in rooted_elems:
    print(r)

model.write("test.ifc")



