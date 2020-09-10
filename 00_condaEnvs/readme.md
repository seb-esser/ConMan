# Installing the anaconda env for CM

## prerequisites
- installed anaconda client

## importing the conda env
- open CMD
- navigate to the folder that contains the `cm_packages.txt` file
- run `conda create --name CM --file cmpackage.txt` in the cmd

## test installation
- start python the created env
- try `import ifcopenshell` 