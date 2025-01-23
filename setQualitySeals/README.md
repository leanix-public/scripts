# Set Quality Seals Script

## Overview

The breakQualitySeal script allows the user to break all quality seals of FactSheets of a given type. To achieve this, the script changes a field named *alias*. This ideally would be changed to a separate field only used for this purpose.

The setAllQualitySeals script allows the user to set all Quality Seals for a FactSheet type specified in the used query.

To achieve all this, the script uses GraphQL queries to both read and write data in the workspace.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Determine the correct FactSheet types.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use either of the following commands:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> FACTSHEET_TYPE=<> python breakQualitySeal.py
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python setAllQualitySeals.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX Quality Seal](https://docs-eam.leanix.net/docs/quality-seal)
