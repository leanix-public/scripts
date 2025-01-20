# Delete Tags Script

## Overview

The deleteTags script allows the user to mass delete Tags based on their id. The Tags are specified in the input file Book1.csv.

The script then deletes the Tags utilizing GraphQL queries.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace for the deletion of multiple Tags.
2. Set up the input file. An example can be found in Book1.csv.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python deleteTag.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX FactSheet Tags](https://docs-eam.leanix.net/docs/tags)
