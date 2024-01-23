import zipfile
from pprint import pprint

from lxml import etree
from xmldiff import main

bcf_init = "sampleData/BCF-sample-topoChange-v1.bcf"
bcf_updt = "sampleData/BCF-sample-topoChange-v2.bcf"

# unzip
for bcf in [bcf_init, bcf_updt]:
    with zipfile.ZipFile(bcf,"r") as zip_ref:
        zip_ref.extractall(bcf[:-3])

# get both markups
markup_path_init = r"sampleData/BCF-sample-topoChange-v1/d2645e77-d21c-4ba8-b078-1c66f1c5bac4/markup.bcf"
markup_path_updt = r"sampleData/BCF-sample-topoChange-v2/d2645e77-d21c-4ba8-b078-1c66f1c5bac4/markup.bcf"

tree_init = etree.parse(markup_path_init)
tree_updt = etree.parse(markup_path_updt)

# run xml diff over markup files
diff_res = main.diff_trees(tree_init, tree_updt, diff_options={"F": 1})

# print the result
pprint(diff_res)


