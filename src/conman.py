""" package import """
import argparse
import glob
import os

from scripts.Commit import commit
from scripts.Fetch import fetch
from scripts.Pull import pull
from scripts.Push import push
from scripts.Remove import remove

""" file import """
import scripts.Ifc2Graph as ifc2graph
import scripts.CityGML2Graph as citygml2graph
import scripts.Graph2Ifc as graph2ifc
from scripts.GetStatus import get_status

parser = argparse.ArgumentParser('ConMan')

# status
parser.add_argument("-s", "--status",
                    action="store_true",
                    help="reports repository status",
                    )

# add file to tracking
parser.add_argument("-a", "--add",
                    type=str,
                    help="add a BIM model (or a new version, respectively) to the repository. -p is required",
                    # choices=["ifc", "citygml", ".bim"]
                    )
# specify location for add function
parser.add_argument("-p", "--path",
                    type=str,
                    help="The path to the file. Can be either path to a file or a directory. "
                         "Should a directory be given, all files of the specified file type will be added.")

# get file from graph
parser.add_argument("-g", "--get",
                    type=str,
                    help="get a BIM model (or a new version, respectively) from the repository "
                         "and create a file representation. -l is required. ",
                    )
# specify graph label for get-function
parser.add_argument("-l", "--label",
                    type=str,
                    help="The label of the neo4j graph")

#remove
parser.add_argument("-rm", "--remove",
                    type=str,
                    help="removes a graph from the database by its timestamp label")

# commit
parser.add_argument("-c", "--commit",
                    type=str,
                    help="generate transformation rules out of the most recent graph and the last committed "
                         "version of a model \n")

# push
parser.add_argument("-push", "--push",
                    action="store_true",
                    help="push transformation rules to server. "
                         "Remote settings to be defined in remoteConfig.txt \n")

# fetch
parser.add_argument("-f", "--fetch",
                    action="store_true",
                    help="fetch transformation rules from server. "
                         "Remote settings to be defined in remoteConfig.txt \n")

# fetch
parser.add_argument("-pull", "--pull",
                    action="store_true",
                    help="apply transformation rules to local repository. "
                         "Remote settings to be defined in remoteConfig.txt \n")

# get the user arguments
args = parser.parse_args()

# check input

if args.status is True:
    get_status()

elif args.add is not None:
    # get path from --p flag and parse model into graph database
    if args.add == "ifc":
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

            ifc2graph.parse(paths)

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

elif args.get is not None:
    # parse graph to file
    label = args.label
    folder = args.path
    if args.get == "ifc":
        graph2ifc.parse(ts=label, directory=folder)

    elif args.get == "citygml":
        raise Exception("Not implemented yet.")

    else:
        raise Exception("Types do not match.")

elif args.remove is not None:
    remove(args.remove)

elif args.commit is not None:
    # calculate diff and prepare patch
    commit(args.commit)

elif args.push is True:
    push()

elif args.pull is True:
    pull()

elif args.fetch is True:
    fetch()
