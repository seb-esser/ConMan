import ifcopenshell


def prepare_ifc():

    model_init = ifcopenshell.open(r"C:\Users\Sebastian Esser\Desktop\wand-tuer\Wand_single.ifc")
    model_updt = ifcopenshell.open(r"C:\Users\Sebastian Esser\Desktop\wand-tuer\Wand_mitTuer.ifc")

    get_rels_init = model_init.by_type("IfcRelationship", include_subtypes=True)
    get_rels_updt = model_updt.by_type("IfcRelationship", include_subtypes=True)

    for rel_entity in get_rels_init:
        guid = rel_entity.GlobalId
        if guid in [x.GlobalId for x in get_rels_updt]:
            # spotted same guid, change both
            new_guid = ifcopenshell.guid.new()

            model_init.by_guid(guid).GlobalId = new_guid
            model_updt.by_guid(guid).GlobalId = new_guid

    model_init.write(r"C:\Users\Sebastian Esser\Desktop\wand-tuer\Wand_single-guidsMod.ifc")
    model_updt.write(r"C:\Users\Sebastian Esser\Desktop\wand-tuer\Wand_mitTuer-guidsMod.ifc")



if __name__ == "__main__":
    prepare_ifc()

