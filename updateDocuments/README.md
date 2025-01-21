# Update Documents Script

## Overview

The updateDocuments script allows the user to update Documents present on certain FactSheets on a larger scale.

In the curren state, the script only updates the URLs set on the Documents, but this can easily be changed to fit your needs.

To achieve this, the script uses GraphQL queries to write data to the workspace.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Prepare your input and change the code to work on the provided data.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
$ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python updateDocuments.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX FactSheet Resources](https://docs-eam.leanix.net/reference/manage-documents-for-a-fact-sheet)
