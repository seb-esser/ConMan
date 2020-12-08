
import requests

class IfcGrGen_SchemaMapper: 

	def __init__(self, version = None):
		self.version_identifier = version

	def load_schema_from_file(self, file_path):
		with open(file_path) as f: 
			self.schema = f.read()

	def load_schema_from_url(self, url):
		print('loading schema definition from server...')
		res_code = requests.get(url).status_code
		res_text = requests.get(url).text

		if res_code == 200:
			print('resonse successful')
			self.schema = res_text

		else:
			print('something went wrong.')
			exit()

	def print_schema(self):
		print(self.schema)

	def split_global_tokens(self):

		global_tokens = self.schema.split('END_')
		print(global_tokens[23])


