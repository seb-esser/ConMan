# Versioning Manager as BIM Level 3 CDE

## Installation and Setup

### Forking the repo

Start with creating a fork of this repository by clicking the fork symbol in the upper right corner. 
You will be asked to specify the target hub (normally, only your personal space can be chosen).
Once forking is done, run `git clone` to download the repo on your machine. 

### Installation and preliminary settings

The codebase acts as an intermediate server between an end-user and a running neo4j graph database. 
Therefore, please download and install the following products on your machine before continuing: 

 - Download and install the latest version of [neo4j Desktop](https://neo4j.com/download-v2/)
   You can test its successful installation by creating and starting a new database instance. 

   Running DB instances are accessible via http on port 7474. 

   Default credentials: 
    user:   `neo4j`
    pw:     `password`

- Download and install [Anaconda](https://www.anaconda.com/products/individual)
    Also check out the installation guidelines provided in `00_condaEnvs` 

    

