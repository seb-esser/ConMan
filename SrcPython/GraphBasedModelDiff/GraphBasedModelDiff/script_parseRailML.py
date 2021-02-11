
import xml.etree.ElementTree as ET 



path = './00_sampleData/RailML_xml/railML_SimpleExample_v11_railML3-1_04.xml'

tree = ET.parse(path)
root = tree.getroot()
for child in root:
	print(child.tag, child.attrib)




