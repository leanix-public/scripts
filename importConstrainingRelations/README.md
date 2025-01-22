# Import Constraining Relations Script

## Overview

The importConstrainingRelations script allows you to import constraining relations from Applications to Business Capabilities based on the given input file.

As an input, you have to provide the IDs of the Application, the Business Capability and the constraining User Group.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Prepare the input file based on the example in *Book2.csv*.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python importConstrainingRelations.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX Constraining Relations](https://docs-eam.leanix.net/docs/adding-and-editing-data-in-fact-sheets)
