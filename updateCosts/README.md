# Update Costs Script

## Overview

The updateCosts script allows the user to make multiple changes to costs set on relations from Applications to ITComponents.

The changes to be made are specified in the Book1.csv file.

To achieve this, the script uses GraphQL queries to write the data to the workspace.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Set up the input file with the correct IDs and values. An example can be found in Book1.csv.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python updateCosts.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
