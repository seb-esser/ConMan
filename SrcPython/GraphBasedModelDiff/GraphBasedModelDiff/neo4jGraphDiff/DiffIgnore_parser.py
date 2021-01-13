
import json

class DiffIgnore: 

	# default constructor
	def __init__(self, ignoreAttrs, ignoreNodeTypes):
		self.ignore_attrs = ignoreAttrs
		self.ignore_node_tpes = ignoreNodeTypes

	# from json factory
	@classmethod
	def from_json(cls, jsonfile): 

		json_content = None
		with open(jsonfile) as f: 
			json_content = json.load(f)

		ignore_labels = json_content["IgnoreNodeTypes"]
		ignore_attrs = json_content["IgnoreNodeAttributes"]

		labels_list = []
		for ignore_label in ignore_labels: 
			labels_list.append(ignore_label)

		attrs_list = []
		for ignore_attr in ignore_attrs: 
			attrs_list.append(ignore_attr)

		return cls(attrs_list, labels_list)