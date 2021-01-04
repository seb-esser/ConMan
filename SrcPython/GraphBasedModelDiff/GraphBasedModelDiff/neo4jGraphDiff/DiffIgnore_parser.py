
import json

class DiffIgnore: 

	# default constructor
	def __init__(self, ignoreAttrs, ignoreNodeTypes):
		self.ignore_attrs = ignoreAttrs
		self.ignore_node_tpes = ignoreNodeTypes

	# from json factory
	@classmethod
	def from_json(cls, jsonfile): 

		json_content = []
		with open(jsonfile) as f: 
			json_content = json.loads(f)

		ignore_labels = json_content["IgnoreNodeLabels"]
		ignore_attrs = json_content["IgnoreNodeAttributes"]

		labels_list = []
		for ignore_label in ignore_labels: 
			labels_list.append(ignore_label)

		attrs_list = []
		for ignore_attr in ignore_attrs: 
			ignore_attr.append(ignore_label)

		return cls(attrs_list, labels_list)