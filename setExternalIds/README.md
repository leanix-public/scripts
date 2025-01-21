# Set External IDs Script

## Overview

The setExternalIds script allows the user to write the External ID of a FactSheet under a given path. 

To achieve this, the script uses GraphQL queries to write the data.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Prepare the input data and provide the FactSheet ID, the path of the field that is to be mutated and the value itself.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> FACTSHEET_ID=<> PATH=<> EXTERNAL_ID=<> python setExternalIds.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
