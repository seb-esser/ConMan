""" package import """
import argparse
import os
import glob

""" file import """
import scripts.Ifc2Graph as ifc2graph
import scripts.CityGML2Graph as citygml2graph
import scripts.Graph2Ifc as graph2ifc
import scripts.GraphBasedModelDiff as graphbaseddiff

# --- Script ---

parser = argparse.ArgumentParser()

# define arguments
parser.add_argument("-i", "--input", type=str,
                    help="Specifies the input type. If 'diff' is selected, all other args will be ignored. Edit diff in scripts/GraphBasedModelDiff.py", choices=["ifc", "citygml", "graph", "diff"])
parser.add_argument("-o", "--output", type=str,
                    help="Specifies the output type.", choices=["ifc", "graph"])
parser.add_argument("-p", "--path", type=str,
                    help="The path to the file. Can be either path to a file or a directory. Should a directory be given all files within that directory will be used.")
parser.add_argument("-l", "--label", type=str,
                    help="The label of the neo4j graph")

# get the user arguments
args = parser.parse_args()

# check input
if args.input == "ifc":
    # check output
    if args.output == "graph":
        # check if the path points to a file or directory
        if os.path.isfile(args.path):
            # execute the corresponding script
            ifc2graph.parse([args.path])

        else:
            paths = []
            # gets all .ifc files in "directory"
            directory = args.path + "/**/*.ifc"
            for filepath in glob.glob(directory, recursive=True):
                paths.append(filepath)
                print(paths)

            ifc2graph.parse(paths)

    else:
        # e.g. input "ifc" and output "ifc"
        raise Exception("Types do not match.")

elif args.input == "citygml":
    if args.output == "graph":
        if os.path.isfile(args.path):
            citygml2graph.parse([args.path])

        else:
            paths = []
            directory = args.path + "/**/*.gml"
            for filepath in glob.glob(directory, recursive=True):
                paths.append(filepath)

            citygml2graph.parse(paths)

    else:
        raise Exception("Types do not match.")
elif args.input == "graph":
    if args.output == "ifc":
        graph2ifc.parse()

    elif args.output == "citygml":
        print("Not implemented yet.")

    else:
        raise Exception("Types do not match.")

# Execute the diff script, all other arguments are ignored in this case
elif args.input == "diff":
    graphbaseddiff.diff()
