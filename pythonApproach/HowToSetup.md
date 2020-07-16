# Setup instructions

Install on your machine:
- Neo4j Server
- anaconda environment manager
- git 
- any Python IDE of your choice (VS code, PyCharm, ...)

##Anaconda Setup: 
this is the place where all Python related things get managed. 
- create new environment (in addition to the base env)
- google for `install ifcopenshell conda` and `install neo4j conda`
- open a commandline tool that refers to the conda env you have recently created
- run commands to install both

## Script setup:
- clone the repo
- open the folder containing all python files with your IDE
- set the interpreter to the python dist inside the conda env
- create a new neo4j database instance and change the password in the connector method (search for password)

## Run the mapping script
- activate the conda env (either via GUI or via cmd `conda activate <envName>`)
- run the script from your IDE or from cmd `<& path to the python.exe inside the env> <path of the mapping script>`