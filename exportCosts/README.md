# Export Costs Script

## Overview

The exportCosts script allows the user to mass export the costs of every Application to ITComponent Relation currently active in the workspace.

The results are retrieved with GraphQL queries and are stored inside *results.csv*.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace and populate each Relation with the correct costs.
2. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python exportCosts.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
