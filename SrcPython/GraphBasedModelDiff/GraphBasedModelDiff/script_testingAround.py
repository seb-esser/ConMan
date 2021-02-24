
import ifcopenshell

path = './00_sampleData/IFC_stepP21/Beam_extrudedGeom/beam-extruded-solid_initial.ifc'

model = ifcopenshell.open(path)

ptList = model.by_type('IfcCartesianPointList')[0]
indexedPolyCurve = model.by_type('IfcIndexedPolyCurve')[0]

for key, val in ptList.__dict__:
	print('{} : {}'.format(key, val))

print()
for key, val in indexedPolyCurve.__dict__:
	print('{} : {}'.format(key, val))

