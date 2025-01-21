# Archive FactSheets Script

## Overview

The archiveFactSheets script allows you to mass delete FactSheets in your workspace. The input file provides all IDs of the FactSheets that are to be deleted.

The script uses GraphQL queries to archive the FactSheets.

## Prerequisites

Before you start, do the following:

1. Create a list of the IDs of the FactSheets you want to delete and provide them in a csv or xlsx file. An example can be found in *Book1.csv*.
2. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python archiveFactsheets.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX Developer Docs](https://docs-eam.leanix.net/docs/archive-delete-and-recover-a-fact-sheet)
