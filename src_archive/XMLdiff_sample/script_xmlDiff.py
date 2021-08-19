


from lxml import etree
from xmldiff import main, formatting


file1 = 'Initial_GeomRepresentation_01.ifcxml'
file2 = 'Update_GeomRepresentation_01.ifcxml'

# create diff
diff = main.diff_files(file1, file2)

for operation in diff:
    print(operation)


