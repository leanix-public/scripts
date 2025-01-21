# Unarchive FactSheets Script

## Overview

The unarchiveFactSheets script allows the user to mass unarchive FactSheets. The FactSheets themselves are specified in *Book1.csv*.

To achieve this, the script uses GraphQL queries to set the status of the FactSheets.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Set up the input file with the correct IDs. An example can be found in *Book1.csv*.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python archive.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX Developer Docs](https://docs-eam.leanix.net/docs/archive-delete-and-recover-a-fact-sheet)
