# Installing the anaconda env for ConsistencyManager

## Prerequisites
- installed anaconda client: visit [Anaconda](https://www.anaconda.com/products/individual), download and install
- make sure you add `conda` to the PATH variable to access conda from any terminal 
<!-- - create a new environment next to the base environment (e.g., use `ConsistencyManager` as the name) -->

## importing the conda env
- open a Terminal/CMD
- navigate to the folder that contains the `cm_packages.yml` file
- run `conda create --file cm_packages.yml` in the cmd

## test installation
- start python the created env using `python3` or `python` (depending if you are on Windows or Linux)
- try python command `import ifcopenshell` 
