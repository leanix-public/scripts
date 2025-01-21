# Create Documents Script

## Overview

The createDocuments script allows the user to create multiple documents based on the input file *URLS.csv*.

The script creates documents for separate documents for the FactSheets specified in this file.

To achieve this, the script uses GraphQL queries to create said documents.

## Prerequisites

Before you start, do the following:

1. Put together the input file based on the example given in *URLS.csv*.
2. Prepare your workspace for the creation of multiple documents.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python createDocuments.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX FactSheet Resources](https://docs-eam.leanix.net/reference/manage-documents-for-a-fact-sheet)
