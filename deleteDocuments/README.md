# Delete Documents Script

## Overview

The deleteDocuments script in the current state allows the user to delete all existing documents from ITComponent FactSheets.

This behaviour can easily be altered to fit your use case by changing the GraphQL query in the script.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace for the creation of multiple documents.
2. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python deleteDocuments.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX FactSheet Resources](https://docs-eam.leanix.net/reference/manage-documents-for-a-fact-sheet)
