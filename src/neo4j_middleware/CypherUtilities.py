
class CypherUtilities:

    @classmethod
    def parse_attrs(cls, all_attributes_raw: list) -> dict:
        """
        translates attributes extracted with regex into full python dicts
        @param all_attributes_raw:
        @return:
        """
        attr_dict = {}
        for t in all_attributes_raw:
            # t is a tuple
            attr_dict[t[0].replace("'", "").replace(" ", "")] = t[1].replace(" ", "")
            # ToDo: cast datatypes properly

        return attr_dict
