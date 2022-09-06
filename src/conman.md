# ConMan CLI

Command line interface to interact with the graph

## getting started

use ``python conman.py --h`` to display the help menu

## Get status

Usage:
``python conman.py -s ``


## Add model to repository

Usage:
``python conman.py -a "<model-type>" -p "<path-to-model-file>"``

Example: 
``python conman.py -a "ifc" -p "C:\dev\myModel.ifc"``

# Get model from repository

Usage:
``python conman.py -g "<model-type>" -l "<timestamp-label>"``

Example:
``python conman.py -g "ifc" -l "ts20220726T075533010"``

# Commit 

Usage: 
``python conman.py -c "<commit-message>" ``

Example:
``python conman.py -c "updates on geometric representation" ``



