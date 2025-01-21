# Import Costs Script

## Overview

The importCosts script allows you to mass import costs based on a given input file.

In the current state, the script creates new FactSheets based on the names given in the input file and then creates a relation between them with the given cost.

To achieve this, the script uses GraphQL queries to perform every necessary mutation.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Prepare the input file based on the example in *Book1.csv*.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python importCosts.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
