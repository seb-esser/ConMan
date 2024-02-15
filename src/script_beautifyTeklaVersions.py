import ifcopenshell

model_v2 = ifcopenshell.open(
    r"C:\Users\sesse\OneDrive - TUM\01_TUMCMS\00_Promotion\dev\00_ArchTW-Kopplung\TW-Model-3\TW-Model\IFC\TW-v2-realExport.ifc")
model_v1 = ifcopenshell.open(
    r"C:\Users\sesse\OneDrive - TUM\01_TUMCMS\00_Promotion\dev\00_ArchTW-Kopplung\TW-Model-3\TW-Model\IFC\Tragwerk-dflt.ifc")

transfer_dict = {}

# extract guids and element_ids from init model
for elem in model_v1.by_type("IfcElement"):

    if elem.get_info()["type"] == "IfcVoidingFeature":
        continue

    # get name and extract Revit elementID
    tu = elem.Name.split(":")
    revit_id = tu[-1]
    name = ":".join(tu[:-1])

    transfer_dict[revit_id] = {"GlobalId": elem.GlobalId, "Name": name}

voiding_transfer_dict = {}

for elem in model_v1.by_type("IfcVoidingFeature"):
    identifier = elem.Description
    voiding_transfer_dict[identifier] = {"GlobalId": elem.GlobalId}

for elem in model_v2.by_type("IfcElement"):

    if elem.get_info()["type"] == "IfcVoidingFeature":
        continue

    # get name and extract Revit elementID
    tu = elem.Name.split(":")
    revit_id = tu[-1]
    name = ":".join(tu[:-1])

    # reset values to initial version
    elem.Name = transfer_dict[revit_id]["Name"] + ":" + revit_id
    elem.GlobalId = transfer_dict[revit_id]["GlobalId"]

# for elem in model_v2.by_type("IfcVoidingFeature"):
#     elem.GlobalId = voiding_transfer_dict[elem.Description]

model_v2.write(
    r"C:\Users\sesse\OneDrive - TUM\01_TUMCMS\00_Promotion\dev\00_ArchTW-Kopplung\TW-Model-3\TW-Model\IFC\TW-v2-realExport-bautified.ifc")
